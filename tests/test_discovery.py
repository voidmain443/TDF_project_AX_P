"""TDD: TDF discovery predicate + filter."""

from tdf_crawler import discovery, parsers
from tdf_crawler.models import FundMeta


def test_is_tdf_keywords():
    assert discovery.is_tdf(FundMeta("X", "교보악사평생든든적격TDF2025증권자투자신탁"))
    assert discovery.is_tdf(FundMeta("X", "KB 온국민 Target Date Fund 2055"))
    assert not discovery.is_tdf(FundMeta("X", "PEI-RICH사모기업인수증권 3"))
    assert not discovery.is_tdf(FundMeta("X", "GB100년공모주증권자투자신탁 1[채권혼합]"))


def test_filter_tdf_on_real_fixture(load_fixture):
    funds, _ = parsers.map_funds_and_navs(load_fixture("stdprice_sample.xml"))
    tdf = discovery.filter_tdf(funds)
    codes = {f.fund_code for f in tdf}
    assert codes == {"K55207CP5413", "K55207CP5447", "K55207CP5488"}  # PEI-RICH excluded
