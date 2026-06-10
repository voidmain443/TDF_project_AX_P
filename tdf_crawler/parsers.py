"""Pure parsers: Proframe XML bytes -> typed records.

No I/O, no network -- the TDD core. ``extract_rows`` is generic (locates the
repeated ``<selectMeta>`` row elements, namespace-agnostic); the typed mappers
apply the positional ``tmpVN`` column maps from :mod:`tdf_crawler.config`.
"""

from __future__ import annotations

import re
from typing import Optional
from xml.etree import ElementTree as ET

from . import config
from .models import FundMeta, NavRecord, FeeRecord

_VINTAGE_RE = re.compile(r"(19|20)\d{2}")


def parse_number(raw: Optional[str]) -> Optional[float]:
    """'1,012.34' / '.14' / '43369' -> float ; '' / '-' / None -> None."""
    if raw is None:
        return None
    s = raw.strip().replace(",", "")
    if s in ("", "-", "N/A"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def parse_date(raw: Optional[str]) -> Optional[str]:
    """'YYYYMMDD' / 'YYYY-MM-DD' / 'YYYY.MM.DD' -> ISO 'YYYY-MM-DD'."""
    if not raw:
        return None
    digits = re.sub(r"\D", "", raw)
    if len(digits) != 8:
        return None
    return f"{digits[0:4]}-{digits[4:6]}-{digits[6:8]}"


def parse_vintage_year(name: str) -> Optional[int]:
    """Extract the target retirement year (e.g. 2045) from a fund name."""
    m = _VINTAGE_RE.search(name or "")
    return int(m.group()) if m else None


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def extract_rows(xml_bytes: bytes, row_tag: str = "selectMeta") -> list[dict]:
    """Return every ``row_tag`` element as a {child_local_name: text} dict."""
    if not xml_bytes or not (xml_bytes.strip() if isinstance(xml_bytes, bytes) else xml_bytes.strip()):
        return []
    root = ET.fromstring(xml_bytes)
    rows: list[dict] = []
    for el in root.iter():
        if _local(el.tag) != row_tag:
            continue
        row = {_local(c.tag): (c.text.strip() if c.text else "") for c in el}
        rows.append(row)
    return rows


def _v(row: dict, col: str) -> Optional[str]:
    val = row.get(col)
    return val if val not in (None, "") else None


def map_funds_and_navs(xml_bytes: bytes) -> tuple[list[FundMeta], list[NavRecord]]:
    """Parse the 펀드기준가격 bulk response into (fund metas, nav records).

    One row yields one FundMeta (identity) and one NavRecord (daily values).
    """
    cols = config.STDPRICE_COLUMNS
    funds: list[FundMeta] = []
    navs: list[NavRecord] = []
    for row in extract_rows(xml_bytes, config.SERVICES["stdprice"].row_tag):
        code = _v(row, cols["fund_code"])
        if not code:
            continue
        name = _v(row, cols["fund_name"]) or ""
        funds.append(FundMeta(
            fund_code=code,
            fund_name=name,
            manager=_v(row, cols["manager"]),
            fund_type=_v(row, cols["fund_type"]),
            vintage_year=parse_vintage_year(name),
        ))
        date = parse_date(_v(row, cols["base_date"]))
        if date:
            navs.append(NavRecord(
                fund_code=code,
                base_date=date,
                nav=parse_number(_v(row, cols["nav"])),
                aum_settlement=parse_number(_v(row, cols["aum_settlement"])),
                net_assets=parse_number(_v(row, cols["net_assets"])),
            ))
    return funds, navs


def map_fees(xml_bytes: bytes, base_date: str) -> list[FeeRecord]:
    """Parse the 보수비용비교 response. ``base_date`` (ISO) is injected as the
    fee rows do not carry a date column."""
    cols = config.FEE_COLUMNS
    out: list[FeeRecord] = []
    for row in extract_rows(xml_bytes, config.SERVICES["fees"].row_tag):
        code = _v(row, cols["fund_code"])
        if not code:
            continue
        out.append(FeeRecord(
            fund_code=code,
            base_date=base_date,
            ter_synthetic=parse_number(_v(row, cols["ter_synthetic"])),
            mgmt_fee=parse_number(_v(row, cols["mgmt_fee"])),
            sales_fee=parse_number(_v(row, cols["sales_fee"])),
        ))
    return out
