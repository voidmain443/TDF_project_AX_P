"""TDD: pure parsers from real KOFIA selectMeta/tmpVN XML -> typed records."""

import pytest

from tdf_crawler import parsers
from tdf_crawler.models import FundMeta, NavRecord, FeeRecord


@pytest.mark.parametrize("raw,expected", [
    ("1,311.35", 1311.35),
    ("7333", 7333.0),
    (".2", 0.2),         # KOFIA fee values come as leading-dot percentages
    (".81", 0.81),
    ("0", 0.0),
    ("", None),
    ("-", None),
    (None, None),
])
def test_parse_number(raw, expected):
    assert parsers.parse_number(raw) == expected


@pytest.mark.parametrize("raw,expected", [
    ("20260604", "2026-06-04"),
    ("2026-06-04", "2026-06-04"),
    ("", None),
])
def test_parse_date(raw, expected):
    assert parsers.parse_date(raw) == expected


def test_extract_rows_counts_selectmeta(load_fixture):
    rows = parsers.extract_rows(load_fixture("stdprice_sample.xml"), "selectMeta")
    assert len(rows) == 4
    assert rows[0]["tmpV12"] == "K55207CP5413"


def test_extract_rows_empty(load_fixture):
    assert parsers.extract_rows(load_fixture("empty_real.xml"), "selectMeta") == []


def test_map_funds_and_navs(load_fixture):
    funds, navs = parsers.map_funds_and_navs(load_fixture("stdprice_sample.xml"))
    assert len(funds) == 4 and len(navs) == 4
    f0 = {f.fund_code: f for f in funds}["K55207CP5413"]
    assert f0.manager == "교보악사자산운용"
    assert f0.vintage_year == 2025          # parsed "TDF2025"
    n0 = {n.fund_code: n for n in navs}["K55207CP5413"]
    assert n0 == NavRecord("K55207CP5413", "2026-06-04",
                           nav=1311.35, aum_settlement=7333.0, net_assets=0.0)


def test_map_fees_injects_base_date(load_fixture):
    fees = parsers.map_fees(load_fixture("fee_sample.xml"), "2026-04-30")
    assert len(fees) == 4
    f = {x.fund_code: x for x in fees}["K55207CP5447"]
    # tmpV12 TER(A+B)=합성총보수, tmpV5 운용보수, tmpV6 판매보수
    assert f == FeeRecord("K55207CP5447", "2026-04-30",
                          ter_synthetic=0.81, mgmt_fee=0.2, sales_fee=0.54)


def test_map_on_empty(load_fixture):
    funds, navs = parsers.map_funds_and_navs(load_fixture("empty_real.xml"))
    assert funds == [] and navs == []
    assert parsers.map_fees(load_fixture("empty_real.xml"), "2026-04-30") == []
