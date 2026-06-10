"""TDD: storage layer -- schema creation, idempotent upserts, run logging."""

from tdf_crawler import db
from tdf_crawler.models import FundMeta, NavRecord, FlowRecord, FeeRecord


def test_init_creates_all_tables(tmp_path):
    conn = db.connect(tmp_path / "t.db")
    db.init_schema(conn)
    names = {row[0] for row in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"funds", "nav_daily", "flows_daily", "fees", "crawl_runs"} <= names


def test_upsert_fund_is_idempotent(tmp_path):
    conn = db.connect(tmp_path / "t.db")
    db.init_schema(conn)
    f = FundMeta("KR123", "삼성 한국형 TDF2045", "삼성자산운용", "주식혼합", 2045)

    db.upsert_funds(conn, [f])
    db.upsert_funds(conn, [f])  # same PK twice

    rows = conn.execute("SELECT fund_code, fund_name, vintage_year FROM funds").fetchall()
    assert rows == [("KR123", "삼성 한국형 TDF2045", 2045)]


def test_upsert_fund_updates_last_seen_and_values(tmp_path):
    conn = db.connect(tmp_path / "t.db")
    db.init_schema(conn)
    db.upsert_funds(conn, [FundMeta("KR1", "old name")])
    db.upsert_funds(conn, [FundMeta("KR1", "new name", manager="KB")])

    name, manager = conn.execute(
        "SELECT fund_name, manager FROM funds WHERE fund_code='KR1'").fetchone()
    assert name == "new name"
    assert manager == "KB"


def test_upsert_nav_idempotent_on_code_and_date(tmp_path):
    conn = db.connect(tmp_path / "t.db")
    db.init_schema(conn)
    db.upsert_navs(conn, [NavRecord("KR1", "2026-06-05", nav=1012.34, net_assets=5e9)])
    # re-run same day with a corrected value -> update, not duplicate
    db.upsert_navs(conn, [NavRecord("KR1", "2026-06-05", nav=1015.00, net_assets=5e9)])

    rows = conn.execute("SELECT base_date, nav FROM nav_daily WHERE fund_code='KR1'").fetchall()
    assert rows == [("2026-06-05", 1015.00)]


def test_upsert_flows_and_fees(tmp_path):
    conn = db.connect(tmp_path / "t.db")
    db.init_schema(conn)
    db.upsert_flows(conn, [FlowRecord("KR1", "2026-06-05", inflow=10.0, outflow=4.0, net_flow=6.0)])
    db.upsert_fees(conn, [FeeRecord("KR1", "2026-06-05", ter_synthetic=0.7, mgmt_fee=0.4)])

    assert conn.execute("SELECT net_flow FROM flows_daily").fetchone()[0] == 6.0
    assert conn.execute("SELECT ter_synthetic FROM fees").fetchone()[0] == 0.7


def test_compute_flows_from_aum_deltas(tmp_path):
    conn = db.connect(tmp_path / "t.db")
    db.init_schema(conn)
    # two consecutive dates with different 설정액 -> net_flow = delta
    db.upsert_navs(conn, [NavRecord("KR1", "2026-06-03", aum_settlement=1000.0)])
    db.upsert_navs(conn, [NavRecord("KR1", "2026-06-04", aum_settlement=1250.0)])

    n = db.compute_and_upsert_flows(conn, "2026-06-04")
    assert n == 1
    net = conn.execute(
        "SELECT net_flow FROM flows_daily WHERE fund_code='KR1' AND base_date='2026-06-04'"
    ).fetchone()[0]
    assert net == 250.0


def test_recompute_all_flows_fills_gaps(tmp_path):
    conn = db.connect(tmp_path / "t.db")
    db.init_schema(conn)
    # three dates loaded out of order; per-date compute on the middle one alone
    # could not see its predecessor. recompute_all_flows fixes every date.
    db.upsert_navs(conn, [NavRecord("KR1", "2026-06-04", aum_settlement=1200.0)])
    db.upsert_navs(conn, [NavRecord("KR1", "2026-06-01", aum_settlement=1000.0)])
    db.upsert_navs(conn, [NavRecord("KR1", "2026-06-02", aum_settlement=1100.0)])

    db.recompute_all_flows(conn)
    flows = dict(conn.execute(
        "SELECT base_date, net_flow FROM flows_daily WHERE fund_code='KR1'"))
    assert flows == {"2026-06-02": 100.0, "2026-06-04": 100.0}  # first date has no prior


def test_compute_flows_first_day_yields_nothing(tmp_path):
    conn = db.connect(tmp_path / "t.db")
    db.init_schema(conn)
    db.upsert_navs(conn, [NavRecord("KR1", "2026-06-04", aum_settlement=1000.0)])
    assert db.compute_and_upsert_flows(conn, "2026-06-04") == 0


def test_crawl_run_logging_roundtrip(tmp_path):
    conn = db.connect(tmp_path / "t.db")
    db.init_schema(conn)
    run_id = db.start_run(conn, "2026-06-05")
    db.finish_run(conn, run_id, status="ok", records_upserted=42)

    status, n = conn.execute(
        "SELECT status, records_upserted FROM crawl_runs WHERE run_id=?", (run_id,)).fetchone()
    assert status == "ok"
    assert n == 42


def test_two_runs_same_day_logged_separately(tmp_path):
    conn = db.connect(tmp_path / "t.db")
    db.init_schema(conn)
    db.finish_run(conn, db.start_run(conn, "2026-06-05"), status="ok", records_upserted=1)
    db.finish_run(conn, db.start_run(conn, "2026-06-05"), status="ok", records_upserted=1)
    assert conn.execute("SELECT COUNT(*) FROM crawl_runs").fetchone()[0] == 2
