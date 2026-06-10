"""TDD: end-to-end ingest with a stub fetcher -> real SQLite + idempotency."""

from tdf_crawler import db, run


def _fetcher(fake_fetcher):
    return fake_fetcher(stdprice="stdprice_sample.xml", fees="fee_sample.xml")


def test_ingest_writes_tdf_data_to_sqlite(tmp_path, fake_fetcher):
    conn = db.connect(tmp_path / "t.db")
    db.init_schema(conn)

    summary = run.ingest(conn, _fetcher(fake_fetcher), "2026-06-04")

    # 3 TDFs in the stdprice fixture (PEI-RICH excluded)
    assert conn.execute("SELECT COUNT(*) FROM funds").fetchone()[0] == 3
    assert conn.execute("SELECT COUNT(*) FROM nav_daily").fetchone()[0] == 3
    nav = conn.execute(
        "SELECT nav, aum_settlement FROM nav_daily WHERE fund_code='K55207CP5413'").fetchone()
    assert nav == (1311.35, 7333.0)
    assert summary["funds"] == 3


def test_fees_filtered_to_discovered_tdf_codes(tmp_path, fake_fetcher):
    conn = db.connect(tmp_path / "t.db")
    db.init_schema(conn)
    run.ingest(conn, _fetcher(fake_fetcher), "2026-06-04")
    # nav TDFs = {5413,5447,5488}; fee fixture TDFs = {5447,5488,5496}
    # -> only the intersection {5447,5488} is stored
    codes = {r[0] for r in conn.execute("SELECT fund_code FROM fees")}
    assert codes == {"K55207CP5447", "K55207CP5488"}


def test_rerun_same_day_is_idempotent(tmp_path, fake_fetcher):
    conn = db.connect(tmp_path / "t.db")
    db.init_schema(conn)
    run.ingest(conn, _fetcher(fake_fetcher), "2026-06-04")
    run.ingest(conn, _fetcher(fake_fetcher), "2026-06-04")

    assert conn.execute("SELECT COUNT(*) FROM nav_daily").fetchone()[0] == 3  # no dupes
    assert conn.execute("SELECT COUNT(*) FROM crawl_runs").fetchone()[0] == 2


def test_flows_derived_across_two_dates(tmp_path, fake_fetcher):
    # The fixture always reports base_date 2026-06-04, so seed a prior date by
    # hand, then ingest -> flows = delta of 설정액.
    conn = db.connect(tmp_path / "t.db")
    db.init_schema(conn)
    from tdf_crawler.models import NavRecord
    db.upsert_navs(conn, [NavRecord("K55207CP5413", "2026-06-03", aum_settlement=7000.0)])

    run.ingest(conn, _fetcher(fake_fetcher), "2026-06-04")
    net = conn.execute(
        "SELECT net_flow FROM flows_daily WHERE fund_code='K55207CP5413'").fetchone()[0]
    assert net == 333.0  # 7333 - 7000


def test_ingest_logs_failure(tmp_path):
    conn = db.connect(tmp_path / "t.db")
    db.init_schema(conn)

    class Boom:
        def fetch(self, spec, params):
            raise RuntimeError("network down")

    try:
        run.ingest(conn, Boom(), "2026-06-04")
    except RuntimeError:
        pass
    status, err = conn.execute("SELECT status, error FROM crawl_runs").fetchone()
    assert status == "error" and "network down" in (err or "")


def test_main_cli_writes_db(tmp_path, monkeypatch, fake_fetcher):
    monkeypatch.setattr(run, "get_fetcher", lambda source, **kw: _fetcher(fake_fetcher))
    dbpath = tmp_path / "cli.db"
    rc = run.main(["--date", "2026-06-04", "--db", str(dbpath)])
    assert rc == 0
    conn = db.connect(dbpath)
    assert conn.execute("SELECT COUNT(*) FROM nav_daily").fetchone()[0] == 3
