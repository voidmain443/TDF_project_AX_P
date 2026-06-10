"""Live smoke test against the real KOFIA site.

Deselected by default (``addopts = -m 'not live'``). Run explicitly:

    python -m pytest -m live
"""

import pytest

from tdf_crawler import collectors, config, discovery
from tdf_crawler.fetchers import HttpFetcher


@pytest.mark.live
def test_stdprice_endpoint_returns_tdf_funds():
    fetcher = HttpFetcher()
    # use a recent weekday; KOFIA publishes prior business day's prices
    funds, navs = collectors.collect_stdprice(fetcher, "2026-06-04")
    assert len(funds) > 1000, "bulk fund list should be large"
    tdf = discovery.filter_tdf(funds)
    assert len(tdf) > 100, "expected hundreds of TDF share classes"
    # nav values should be populated for TDFs
    tdf_codes = {f.fund_code for f in tdf}
    tdf_navs = [n for n in navs if n.fund_code in tdf_codes and n.nav]
    assert tdf_navs, "TDF funds should have 기준가 values"
