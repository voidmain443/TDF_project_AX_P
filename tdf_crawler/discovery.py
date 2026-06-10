"""Identify which funds are TDFs.

Discovery is folded into the 펀드기준가격 bulk call (one request returns every
fund, ~26k rows), so this module is just the TDF predicate + filter.
"""

from __future__ import annotations

from . import config
from .models import FundMeta


def is_tdf(fund: FundMeta) -> bool:
    """True if the fund name contains a TDF keyword (case-insensitive)."""
    name = (fund.fund_name or "").upper()
    return any(kw.upper() in name for kw in config.TDF_NAME_KEYWORDS)


def filter_tdf(funds: list[FundMeta]) -> list[FundMeta]:
    return [f for f in funds if is_tdf(f)]
