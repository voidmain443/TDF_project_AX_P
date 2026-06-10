"""Historical backfill: accumulate ALL past TDF snapshots into SQLite.

Strategy (efficient + idempotent + resumable):
  * Prices/flows: one bulk 기준가격 call PER BUSINESS DAY, oldest -> newest
    (chronological so each day's flow = Δ설정액 vs the day before).
  * Fees: published monthly, so ONE call PER MONTH-END (not per day).
  * Re-running skips days/months already stored (``--resume``, default on), so a
    long backfill can be interrupted and continued freely.

Usage:
    python -m tdf_crawler.backfill --start 2020-01-01 --end 2026-06-04
    python -m tdf_crawler.backfill --start 2026-05-01            # end defaults to today (KST)
    python -m tdf_crawler.backfill --start 2026-05-01 --no-fees --delay 2

Note: each business-day call downloads the full ~36 MB all-funds response, so a
multi-year backfill is large/slow. Use --delay to stay polite to KOFIA.
"""

from __future__ import annotations

import argparse
import calendar
import logging
import sqlite3
import sys
import time
from datetime import date, datetime, timedelta, timezone

from . import config, db, run
from .fetchers import get_fetcher
from .fetchers.base import Fetcher

log = logging.getLogger("tdf_crawler.backfill")
_KST = timezone(timedelta(hours=9))


# --- date helpers ------------------------------------------------------------

def business_days(start: str, end: str) -> list[str]:
    """ISO dates Mon–Fri in [start, end], chronological."""
    d, last = date.fromisoformat(start), date.fromisoformat(end)
    out = []
    while d <= last:
        if d.weekday() < 5:  # 0=Mon .. 4=Fri
            out.append(d.isoformat())
        d += timedelta(days=1)
    return out


def month_ends(start: str, end: str) -> list[str]:
    """ISO month-end dates that fall within [start, end], chronological."""
    s, e = date.fromisoformat(start), date.fromisoformat(end)
    out = []
    y, m = s.year, s.month
    while (y, m) <= (e.year, e.month):
        me = date(y, m, calendar.monthrange(y, m)[1])
        if s <= me <= e:
            out.append(me.isoformat())
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


def _completed_price_dates(conn: sqlite3.Connection) -> set[str]:
    """Dates already attempted for prices (ok or holiday/empty) -> skip on resume."""
    rows = conn.execute(
        "SELECT DISTINCT run_date FROM crawl_runs WHERE status IN ('ok','empty')")
    return {r[0] for r in rows}


def _fee_dates_present(conn: sqlite3.Connection) -> set[str]:
    return {r[0] for r in conn.execute("SELECT DISTINCT base_date FROM fees")}


def _tdf_codes(conn: sqlite3.Connection) -> set[str]:
    return {r[0] for r in conn.execute("SELECT fund_code FROM funds")}


# --- backfill ----------------------------------------------------------------

def backfill(conn: sqlite3.Connection, fetcher: Fetcher, start: str, end: str,
             *, fees: bool = True, resume: bool = True, delay: float = 1.5) -> dict:
    db.init_schema(conn)
    days = business_days(start, end)
    done = _completed_price_dates(conn) if resume else set()
    todo = [d for d in days if d not in done]
    log.info("price backfill: %d business days in range, %d to do (%d already done)",
             len(days), len(todo), len(days) - len(todo))

    totals = {"days_done": 0, "days_empty": 0, "nav": 0}
    for i, d in enumerate(todo, 1):
        run_id = db.start_run(conn, d)
        try:
            _codes, summary = run.store_prices(conn, fetcher, d)
            status = "ok" if summary["nav"] > 0 else "empty"
            db.finish_run(conn, run_id, status=status,
                          records_upserted=summary.get("upserted", 0))
            totals["nav"] += summary["nav"]
            totals["days_done" if status == "ok" else "days_empty"] += 1
            log.info("[%d/%d] %s -> %s (nav=%d)", i, len(todo), d, status, summary["nav"])
        except Exception as exc:  # noqa: BLE001
            db.finish_run(conn, run_id, status="error", error=str(exc))
            log.exception("price backfill failed for %s", d)
        if delay:
            time.sleep(delay)

    # Recompute flows across ALL dates so any date stored before its predecessor
    # gets a correct Δ설정액 (fills gaps from earlier standalone runs).
    totals["flows"] = db.recompute_all_flows(conn)
    log.info("recomputed flows for all dates: %d rows", totals["flows"])

    if fees:
        codes = _tdf_codes(conn)
        present = _fee_dates_present(conn) if resume else set()
        me_todo = [m for m in month_ends(start, end) if m not in present]
        log.info("fee backfill: %d month-ends to do", len(me_todo))
        fee_total = 0
        for j, me in enumerate(me_todo, 1):
            try:
                n = run.store_fees_for_date(conn, fetcher, me, codes)
                fee_total += n
                log.info("[fee %d/%d] %s -> %d rows", j, len(me_todo), me, n)
            except Exception:  # noqa: BLE001
                log.exception("fee backfill failed for %s", me)
            if delay:
                time.sleep(delay)
        totals["fees"] = fee_total

    log.info("backfill complete: %s", totals)
    return totals


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="tdf-backfill", description="Accumulate historical KOFIA TDF data into SQLite.")
    p.add_argument("--start", required=True, help="first date YYYY-MM-DD")
    p.add_argument("--end", default=None, help="last date YYYY-MM-DD (default: today KST)")
    p.add_argument("--db", dest="db_path", default=str(config.DEFAULT_DB_PATH))
    p.add_argument("--source", choices=["http", "selenium"], default="http")
    p.add_argument("--no-fees", action="store_true", help="skip 보수 backfill")
    p.add_argument("--no-resume", action="store_true", help="re-fetch already-stored dates")
    p.add_argument("--delay", type=float, default=1.5, help="seconds between requests")
    p.add_argument("-v", "--verbose", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    end = args.end or datetime.now(_KST).date().isoformat()
    conn = db.connect(args.db_path)
    fetcher = get_fetcher(args.source)
    try:
        totals = backfill(conn, fetcher, args.start, end,
                          fees=not args.no_fees, resume=not args.no_resume, delay=args.delay)
    finally:
        close = getattr(fetcher, "close", None)
        if callable(close):
            close()
    print(f"OK backfill {args.start}..{end}: {totals}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
