"""Typed records that mirror the SQLite schema.

Keeping these as plain dataclasses (no behaviour) makes parsers pure and
trivially testable: a parser takes bytes -> list[<one of these>].
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class FundMeta:
    """Identity of a TDF, discovered from the fund list."""

    fund_code: str          # KR standard code, e.g. "KR5370...."
    fund_name: str
    manager: Optional[str] = None       # 운용사
    fund_type: Optional[str] = None     # 펀드유형
    vintage_year: Optional[int] = None  # target retirement year parsed from name (e.g. 2045)


@dataclass(frozen=True)
class NavRecord:
    """Daily price / size snapshot for one fund (기준가 · 설정액 · 순자산)."""

    fund_code: str
    base_date: str          # ISO "YYYY-MM-DD"
    nav: Optional[float] = None             # 기준가격 (per 1,000 좌 or 1 좌, as published)
    aum_settlement: Optional[float] = None  # 설정액 (KRW)
    net_assets: Optional[float] = None      # 순자산총액 (KRW)


@dataclass(frozen=True)
class FlowRecord:
    """Daily fund flow (자금 유출입: 설정/해지)."""

    fund_code: str
    base_date: str
    inflow: Optional[float] = None      # 설정액 증가 (유입)
    outflow: Optional[float] = None     # 해지액 (유출)
    net_flow: Optional[float] = None    # 순유입 (= inflow - outflow when both present)


@dataclass(frozen=True)
class FeeRecord:
    """Fee snapshot (합성 총보수 및 구성)."""

    fund_code: str
    base_date: str
    ter_synthetic: Optional[float] = None  # 합성 총보수 (%, 연)
    mgmt_fee: Optional[float] = None       # 운용보수 (%)
    sales_fee: Optional[float] = None      # 판매보수 (%)
