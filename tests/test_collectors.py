"""TDD: collectors fetch+parse each feed (fetcher mocked)."""

from tdf_crawler import collectors


def test_collect_stdprice_returns_funds_and_navs(fake_fetcher):
    fetcher = fake_fetcher(stdprice="stdprice_sample.xml")
    funds, navs = collectors.collect_stdprice(fetcher, "2026-06-04")
    assert len(funds) == 4 and len(navs) == 4
    svc, params = fetcher.calls[0]
    assert svc == "DISFundStdPriceSO"
    assert params == {"tmpV30": "20260604", "tmpV11": ""}  # bulk: all companies


def test_collect_fees_resolves_month_end(fake_fetcher):
    fetcher = fake_fetcher(fees="fee_sample.xml")
    fees, fee_date = collectors.collect_fees(fetcher, "2026-06-05")
    # first month-end candidate for June is 2026-06-30, fixture returns rows there
    assert fee_date == "2026-06-30"
    assert all(f.base_date == "2026-06-30" for f in fees)
    assert len(fees) == 4


def test_collect_fees_walks_back_when_empty(fake_fetcher):
    # fee service returns empty -> no date resolves
    fetcher = fake_fetcher(fees="empty_real.xml")
    fees, fee_date = collectors.collect_fees(fetcher, "2026-06-05", months_back=3)
    assert fees == [] and fee_date is None
    assert len(fetcher.calls) == 3  # tried 3 month-ends


def test_month_end_candidates():
    assert collectors._month_end_candidates("2026-06-05", 3) == [
        "2026-06-30", "2026-05-31", "2026-04-30"]
