"""SQLite storage: schema + idempotent upserts.

Every write is an ``INSERT ... ON CONFLICT DO UPDATE`` so re-running a day's
crawl never duplicates rows -- it just refreshes values. This is what makes
the daily job safe to retry.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence, Union

from .models import FundMeta, NavRecord, FlowRecord, FeeRecord

_SCHEMA = """
CREATE TABLE IF NOT EXISTS funds (
    fund_code    TEXT PRIMARY KEY,
    fund_name    TEXT NOT NULL,
    manager      TEXT,
    fund_type    TEXT,
    vintage_year INTEGER,
    first_seen   TEXT NOT NULL,
    last_seen    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS nav_daily (
    fund_code      TEXT NOT NULL,
    base_date      TEXT NOT NULL,
    nav            REAL,
    aum_settlement REAL,
    net_assets     REAL,
    PRIMARY KEY (fund_code, base_date)
);

CREATE TABLE IF NOT EXISTS flows_daily (
    fund_code TEXT NOT NULL,
    base_date TEXT NOT NULL,
    inflow    REAL,
    outflow   REAL,
    net_flow  REAL,
    PRIMARY KEY (fund_code, base_date)
);

CREATE TABLE IF NOT EXISTS fees (
    fund_code     TEXT NOT NULL,
    base_date     TEXT NOT NULL,
    ter_synthetic REAL,
    mgmt_fee      REAL,
    sales_fee     REAL,
    PRIMARY KEY (fund_code, base_date)
);

CREATE TABLE IF NOT EXISTS crawl_runs (
    run_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    run_date         TEXT NOT NULL,
    started_at       TEXT NOT NULL,
    finished_at      TEXT,
    status           TEXT,
    records_upserted INTEGER,
    error            TEXT
);

CREATE INDEX IF NOT EXISTS ix_nav_date   ON nav_daily (base_date);
CREATE INDEX IF NOT EXISTS ix_flows_date ON flows_daily (base_date);
CREATE INDEX IF NOT EXISTS ix_fees_date  ON fees (base_date);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def connect(db_path: Union[str, Path]) -> sqlite3.Connection:
    path = Path(db_path)
    if path.parent and not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(_SCHEMA)
    conn.commit()


# --- upserts -----------------------------------------------------------------

def upsert_funds(conn: sqlite3.Connection, funds: Iterable[FundMeta]) -> int:
    now = _now()
    n = 0
    for f in funds:
        conn.execute(
            """
            INSERT INTO funds (fund_code, fund_name, manager, fund_type,
                               vintage_year, first_seen, last_seen)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(fund_code) DO UPDATE SET
                fund_name    = excluded.fund_name,
                manager      = COALESCE(excluded.manager, funds.manager),
                fund_type    = COALESCE(excluded.fund_type, funds.fund_type),
                vintage_year = COALESCE(excluded.vintage_year, funds.vintage_year),
                last_seen    = excluded.last_seen
            """,
            (f.fund_code, f.fund_name, f.manager, f.fund_type,
             f.vintage_year, now, now),
        )
        n += 1
    conn.commit()
    return n


def upsert_navs(conn: sqlite3.Connection, records: Iterable[NavRecord]) -> int:
    n = 0
    for r in records:
        conn.execute(
            """
            INSERT INTO nav_daily (fund_code, base_date, nav, aum_settlement, net_assets)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(fund_code, base_date) DO UPDATE SET
                nav            = COALESCE(excluded.nav, nav_daily.nav),
                aum_settlement = COALESCE(excluded.aum_settlement, nav_daily.aum_settlement),
                net_assets     = COALESCE(excluded.net_assets, nav_daily.net_assets)
            """,
            (r.fund_code, r.base_date, r.nav, r.aum_settlement, r.net_assets),
        )
        n += 1
    conn.commit()
    return n


def upsert_flows(conn: sqlite3.Connection, records: Iterable[FlowRecord]) -> int:
    n = 0
    for r in records:
        conn.execute(
            """
            INSERT INTO flows_daily (fund_code, base_date, inflow, outflow, net_flow)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(fund_code, base_date) DO UPDATE SET
                inflow   = COALESCE(excluded.inflow, flows_daily.inflow),
                outflow  = COALESCE(excluded.outflow, flows_daily.outflow),
                net_flow = COALESCE(excluded.net_flow, flows_daily.net_flow)
            """,
            (r.fund_code, r.base_date, r.inflow, r.outflow, r.net_flow),
        )
        n += 1
    conn.commit()
    return n


def upsert_fees(conn: sqlite3.Connection, records: Iterable[FeeRecord]) -> int:
    n = 0
    for r in records:
        conn.execute(
            """
            INSERT INTO fees (fund_code, base_date, ter_synthetic, mgmt_fee, sales_fee)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(fund_code, base_date) DO UPDATE SET
                ter_synthetic = COALESCE(excluded.ter_synthetic, fees.ter_synthetic),
                mgmt_fee      = COALESCE(excluded.mgmt_fee, fees.mgmt_fee),
                sales_fee     = COALESCE(excluded.sales_fee, fees.sales_fee)
            """,
            (r.fund_code, r.base_date, r.ter_synthetic, r.mgmt_fee, r.sales_fee),
        )
        n += 1
    conn.commit()
    return n


def compute_and_upsert_flows(conn: sqlite3.Connection, base_date: str) -> int:
    """Derive fund flow for ``base_date`` as the change in 설정액 (aum_settlement)
    versus each fund's previous available date, and upsert into flows_daily.

    KOFIA does not expose a clean daily per-fund 설정/해지 amount on these pages,
    so net_flow is the standard proxy: Δ설정원본 (백만원). inflow/outflow stay NULL.
    """
    cur = conn.execute(
        """
        INSERT INTO flows_daily (fund_code, base_date, net_flow)
        SELECT t.fund_code, t.base_date, (t.aum_settlement - p.aum_settlement)
        FROM nav_daily t
        JOIN nav_daily p
          ON p.fund_code = t.fund_code
         AND p.base_date = (SELECT MAX(x.base_date) FROM nav_daily x
                             WHERE x.fund_code = t.fund_code AND x.base_date < t.base_date)
        WHERE t.base_date = ?
          AND t.aum_settlement IS NOT NULL AND p.aum_settlement IS NOT NULL
        ON CONFLICT(fund_code, base_date) DO UPDATE SET net_flow = excluded.net_flow
        """,
        (base_date,),
    )
    conn.commit()
    return cur.rowcount if cur.rowcount and cur.rowcount > 0 else 0


def recompute_all_flows(conn: sqlite3.Connection) -> int:
    """Recompute net_flow for EVERY date against each fund's previous date.

    Needed after a backfill, where some dates were stored before their
    predecessors existed (so their flow couldn't be computed at the time).
    """
    cur = conn.execute(
        """
        INSERT INTO flows_daily (fund_code, base_date, net_flow)
        SELECT t.fund_code, t.base_date, (t.aum_settlement - p.aum_settlement)
        FROM nav_daily t
        JOIN nav_daily p
          ON p.fund_code = t.fund_code
         AND p.base_date = (SELECT MAX(x.base_date) FROM nav_daily x
                             WHERE x.fund_code = t.fund_code AND x.base_date < t.base_date)
        WHERE t.aum_settlement IS NOT NULL AND p.aum_settlement IS NOT NULL
        ON CONFLICT(fund_code, base_date) DO UPDATE SET net_flow = excluded.net_flow
        """,
    )
    conn.commit()
    return cur.rowcount if cur.rowcount and cur.rowcount > 0 else 0


# --- run logging -------------------------------------------------------------

def start_run(conn: sqlite3.Connection, run_date: str) -> int:
    cur = conn.execute(
        "INSERT INTO crawl_runs (run_date, started_at, status) VALUES (?, ?, 'running')",
        (run_date, _now()),
    )
    conn.commit()
    return int(cur.lastrowid)


def finish_run(conn: sqlite3.Connection, run_id: int, *, status: str,
               records_upserted: int = 0, error: str | None = None) -> None:
    conn.execute(
        """
        UPDATE crawl_runs
           SET finished_at = ?, status = ?, records_upserted = ?, error = ?
         WHERE run_id = ?
        """,
        (_now(), status, records_upserted, error, run_id),
    )
    conn.commit()
