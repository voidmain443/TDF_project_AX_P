"""Collectors: fetch + parse each feed for a given date.

Both feeds are queried in bulk (empty company code -> every fund), then the
caller filters to TDFs. Fees are published monthly, so ``collect_fees`` walks
back to the most recent month-end that actually has data.
"""

from __future__ import annotations

import calendar
from datetime import date, datetime

from . import config, parsers
from .fetchers.base import Fetcher
from .models import FundMeta, NavRecord, FeeRecord


def _ymd(base_date: str) -> str:
    return base_date.replace("-", "")


def collect_stdprice(fetcher: Fetcher, base_date: str) -> tuple[list[FundMeta], list[NavRecord]]:
    """Bulk 펀드기준가격: returns (all fund metas, all nav records) for the date."""
    spec = config.SERVICES["stdprice"]
    raw = fetcher.fetch(spec, config.date_params(_ymd(base_date)))
    return parsers.map_funds_and_navs(raw)


def _month_end_candidates(base_date: str, months_back: int = 4) -> list[str]:
    """ISO month-end dates: the base date's month-end, then previous months."""
    d = datetime.strptime(base_date, "%Y-%m-%d").date()
    out: list[str] = []
    y, m = d.year, d.month
    for _ in range(months_back):
        last = calendar.monthrange(y, m)[1]
        out.append(date(y, m, last).isoformat())
        m -= 1
        if m == 0:
            y, m = y - 1, 12
    return out


def collect_fees(fetcher: Fetcher, base_date: str,
                 months_back: int = 4) -> tuple[list[FeeRecord], str | None]:
    """Bulk 보수비용비교. Fees publish monthly, so try month-ends newest-first
    until one returns rows. Returns (records, resolved_date) or ([], None)."""
    spec = config.SERVICES["fees"]
    for cand in _month_end_candidates(base_date, months_back):
        raw = fetcher.fetch(spec, config.date_params(_ymd(cand)))
        recs = parsers.map_fees(raw, cand)
        if recs:
            return recs, cand
    return [], None
