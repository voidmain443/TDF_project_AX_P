"""CLI entrypoint + ingest orchestration for the daily TDF crawl.

Run once a day (e.g. via Windows Task Scheduler):

    python -m tdf_crawler.run

What it does each run (see DATA.md for the full model):
  1. ONE bulk 펀드기준가격 call -> every fund's 기준가/설정액/순자산 for the date.
  2. Keep only TDFs (name match); upsert fund identities + that day's nav row.
  3. Derive fund flow = Δ설정액 vs the fund's previous stored date.
  4. ONE bulk 보수비용비교 call (latest month-end with data) -> TDF 합성총보수.
Every write is an upsert, so re-running a date refreshes values, never dupes.
"""

from __future__ import annotations

import argparse
import logging
import sqlite3
import sys
from datetime import datetime, timezone, timedelta

from . import collectors, config, db, discovery
from .fetchers import get_fetcher
from .fetchers.base import Fetcher

log = logging.getLogger("tdf_crawler")
_KST = timezone(timedelta(hours=9))


def today_kst() -> str:
    return datetime.now(_KST).date().isoformat()


# --- reusable store helpers (shared by daily run + historical backfill) -------

def store_prices(conn: sqlite3.Connection, fetcher: Fetcher, base_date: str,
                 *, dry_run: bool = False) -> tuple[set[str], dict]:
    """One bulk 기준가격 call -> upsert TDF funds + nav + derived flows.

    Returns (tdf_codes, summary). Does NOT touch fees -- callers handle fees on
    their own cadence (daily=latest month-end; backfill=once per month).
    """
    all_funds, all_navs = collectors.collect_stdprice(fetcher, base_date)
    tdf_funds = discovery.filter_tdf(all_funds)
    tdf_codes = {f.fund_code for f in tdf_funds}
    navs = [n for n in all_navs if n.fund_code in tdf_codes]
    log.info("scanned %d funds, %d TDFs, %d nav rows for %s",
             len(all_funds), len(tdf_funds), len(navs), base_date)

    summary = {"funds": len(tdf_funds), "nav": len(navs)}
    if dry_run:
        return tdf_codes, summary

    n = db.upsert_funds(conn, tdf_funds) + db.upsert_navs(conn, navs)
    flows_n = db.compute_and_upsert_flows(conn, base_date)
    summary.update(flows=flows_n, upserted=n + flows_n)
    return tdf_codes, summary


def store_fees_for_date(conn: sqlite3.Connection, fetcher: Fetcher, fee_date: str,
                        tdf_codes: set[str] | None = None) -> int:
    """Fetch + upsert the 보수 table for an explicit month-end date. Returns rows."""
    from . import parsers
    raw = fetcher.fetch(config.SERVICES["fees"], config.date_params(fee_date.replace("-", "")))
    fees = parsers.map_fees(raw, fee_date)
    if tdf_codes is not None:
        fees = [f for f in fees if f.fund_code in tdf_codes]
    return db.upsert_fees(conn, fees)


def ingest(conn: sqlite3.Connection, fetcher: Fetcher, base_date: str,
           *, dry_run: bool = False) -> dict:
    """Daily run: store the day's nav/flows + the latest available 보수 snapshot."""
    run_id = db.start_run(conn, base_date)
    try:
        tdf_codes, summary = store_prices(conn, fetcher, base_date, dry_run=dry_run)

        # fees: monthly; resolve the latest month-end that actually has data
        all_fees, fee_date = collectors.collect_fees(fetcher, base_date)
        fees = [f for f in all_fees if f.fund_code in tdf_codes]
        summary["fees"] = len(fees)
        summary["fee_date"] = fee_date
        log.info("fees: %d TDF rows (as of %s)", len(fees), fee_date)

        if dry_run:
            db.finish_run(conn, run_id, status="dry-run", records_upserted=0)
            log.info("dry-run: %s", summary)
            return summary

        n = summary.get("upserted", 0) + db.upsert_fees(conn, fees)
        summary["upserted"] = n
        db.finish_run(conn, run_id, status="ok", records_upserted=n)
        log.info("ingest ok for %s: %s", base_date, summary)
        return summary
    except Exception as exc:  # noqa: BLE001 -- record every failure
        db.finish_run(conn, run_id, status="error", error=str(exc))
        log.exception("ingest failed for %s", base_date)
        raise


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="tdf-crawl", description="Crawl KOFIA TDF disclosures into SQLite.")
    p.add_argument("--source", choices=["http", "selenium"], default="http")
    p.add_argument("--date", default=None, help="base date YYYY-MM-DD (default: today KST)")
    p.add_argument("--db", dest="db_path", default=str(config.DEFAULT_DB_PATH))
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("-v", "--verbose", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    base_date = args.date or today_kst()
    conn = db.connect(args.db_path)
    db.init_schema(conn)
    fetcher = get_fetcher(args.source)
    try:
        summary = ingest(conn, fetcher, base_date, dry_run=args.dry_run)
    except Exception as exc:  # noqa: BLE001
        print(f"FAILED: {exc}", file=sys.stderr)
        return 1
    finally:
        close = getattr(fetcher, "close", None)
        if callable(close):
            close()
    print(f"OK {base_date}: {summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
