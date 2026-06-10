"""저장 — sqlite에 멱등 upsert (레슨 05~06). PK로 중복 방지."""
import sqlite3
from . import config


def connect() -> sqlite3.Connection:
    con = sqlite3.connect(config.DB)
    con.execute("""
        CREATE TABLE IF NOT EXISTS tdf_nav (
            fund_code TEXT,
            base_date TEXT,
            fund_name TEXT,
            company   TEXT,
            nav       REAL,
            aum       REAL,
            PRIMARY KEY (fund_code, base_date)   -- 한 펀드 × 한 날 = 한 행
        )
    """)
    return con


def save(con: sqlite3.Connection, rows: list[dict]) -> None:
    con.executemany("""
        INSERT INTO tdf_nav (fund_code, base_date, fund_name, company, nav, aum)
        VALUES (:code, :date, :name, :company, :nav, :aum)
        ON CONFLICT(fund_code, base_date) DO UPDATE SET   -- 있으면 덮어쓰기(멱등)
            fund_name=excluded.fund_name, company=excluded.company,
            nav=excluded.nav, aum=excluded.aum
    """, [r for r in rows if r["code"] and r["date"]])
    con.commit()
