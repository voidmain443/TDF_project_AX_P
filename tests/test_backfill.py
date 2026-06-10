"""TDD: historical backfill -- date iteration, resume-skip, end-to-end."""

from tdf_crawler import backfill, db


# --- date helpers ------------------------------------------------------------

def test_business_days_skips_weekends():
    # 2026-06-04 Thu, 05 Fri, 06 Sat, 07 Sun, 08 Mon
    days = backfill.business_days("2026-06-04", "2026-06-08")
    assert days == ["2026-06-04", "2026-06-05", "2026-06-08"]


def test_month_ends_in_range():
    assert backfill.month_ends("2026-04-15", "2026-06-10") == ["2026-04-30", "2026-05-31"]


def test_month_ends_single_partial_month():
    # no month-end falls inside this window
    assert backfill.month_ends("2026-06-01", "2026-06-10") == []


# --- end-to-end with a stub fetcher -----------------------------------------

class _DateAwareFetcher:
    """Returns the stdprice fixture but rewrites its base_date (tmpV14) to match
    the requested tmpV30, so each backfilled day lands on its own date. Fees
    fixture returned as-is."""

    def __init__(self, stdprice_bytes, fee_bytes):
        self.stdprice = stdprice_bytes
        self.fee = fee_bytes
        self.calls = []

    def fetch(self, spec, params):
        self.calls.append((spec.service_name, params))
        if spec.service_name == "DISFundStdPriceSO":
            ymd = params["tmpV30"]
            return self.stdprice.replace(b"<tmpV14>20260604</tmpV14>",
                                         b"<tmpV14>%b</tmpV14>" % ymd.encode())
        return self.fee


def _fetcher(load_fixture):
    return _DateAwareFetcher(load_fixture("stdprice_sample.xml"),
                             load_fixture("fee_sample.xml"))


def test_backfill_accumulates_multiple_dates(tmp_path, load_fixture):
    conn = db.connect(tmp_path / "t.db")
    f = _fetcher(load_fixture)
    backfill.backfill(conn, f, "2026-06-02", "2026-06-04", fees=False, delay=0)

    dates = [r[0] for r in conn.execute(
        "SELECT DISTINCT base_date FROM nav_daily ORDER BY base_date")]
    assert dates == ["2026-06-02", "2026-06-03", "2026-06-04"]  # 3 business days
    # 3 TDF funds x 3 days
    assert conn.execute("SELECT COUNT(*) FROM nav_daily").fetchone()[0] == 9


def test_backfill_resume_skips_done_dates(tmp_path, load_fixture):
    conn = db.connect(tmp_path / "t.db")
    f = _fetcher(load_fixture)
    backfill.backfill(conn, f, "2026-06-02", "2026-06-04", fees=False, delay=0)
    first_calls = len(f.calls)

    # second run with resume should make no new price calls
    backfill.backfill(conn, f, "2026-06-02", "2026-06-04", fees=False, delay=0)
    assert len(f.calls) == first_calls


def test_backfill_derives_flows_chronologically(tmp_path, load_fixture):
    conn = db.connect(tmp_path / "t.db")
    f = _fetcher(load_fixture)
    backfill.backfill(conn, f, "2026-06-02", "2026-06-04", fees=False, delay=0)
    # flows exist for the 2nd and 3rd days (Δ설정액 vs previous business day = 0 here)
    flow_dates = {r[0] for r in conn.execute("SELECT DISTINCT base_date FROM flows_daily")}
    assert "2026-06-03" in flow_dates and "2026-06-04" in flow_dates


def test_backfill_fees_once_per_month_end(tmp_path, load_fixture):
    conn = db.connect(tmp_path / "t.db")
    f = _fetcher(load_fixture)
    backfill.backfill(conn, f, "2026-04-20", "2026-06-04", fees=True, delay=0)
    fee_calls = [c for c in f.calls if c[0] == "DISFundFeeCmsSO"]
    # month-ends in range: 2026-04-30, 2026-05-31  -> 2 fee calls
    assert len(fee_calls) == 2
    fee_dates = {r[0] for r in conn.execute("SELECT DISTINCT base_date FROM fees")}
    assert fee_dates == {"2026-04-30", "2026-05-31"}
