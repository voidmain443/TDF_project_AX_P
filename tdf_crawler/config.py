"""Central configuration: all KOFIA-specific, change-prone knobs live here.

The KOFIA disclosure site (dis.kofia.or.kr) is a WebSquare + Proframe app. Its
grids POST a Proframe XML envelope to a backend gateway and render the returned
rows. The exact gateway URL, service ids and the positional ``tmpVN`` column
layout below were confirmed by a live capture (see ``sniff.py`` / README). When
they change, only this file needs editing -- parsers/storage stay put.

Key facts confirmed from live traffic:
  * Gateway is /proframe**W**eb/XMLSERVICES/ (capital W; lowercase 307-redirects
    to the dead OpenAPI error page -- that was the original "0 rows" bug).
  * Every data grid posts a <DISCondFuncDTO> with tmpV30=date, tmpV11=company
    code (EMPTY = all companies -> one bulk call returns every fund).
  * Responses wrap each row in <selectMeta> with positional columns tmpV1..tmpVN.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

# --- Storage -----------------------------------------------------------------
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = Path(os.environ.get("TDF_DB_PATH", WORKSPACE_ROOT / "data" / "tdf.db"))

# --- Network -----------------------------------------------------------------
BASE_URL = "https://dis.kofia.or.kr"
# NOTE capital W. Override via env once re-captured if KOFIA changes it.
XML_GATEWAY = os.environ.get("TDF_XML_GATEWAY", f"{BASE_URL}/proframeWeb/XMLSERVICES/")
DEFAULT_TIMEOUT = 120  # seconds (bulk all-fund response is ~36 MB)
MAX_RETRIES = 3
RETRY_BACKOFF = 2.0

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) tdf-crawler/0.2",
    "Content-Type": "application/xml; charset=UTF-8",
    "Referer": f"{BASE_URL}/",
}

APP_NAME = "FS-DIS2"


@dataclass(frozen=True)
class ServiceSpec:
    """One Proframe service call: header names + input DTO + row tag in the reply."""

    app_name: str
    service_name: str
    function_name: str
    input_dto: str
    row_tag: str


SERVICES = {
    # 펀드기준가격: discovery + 기준가 + 설정액 + 순자산 (one bulk call/day)
    "stdprice": ServiceSpec(APP_NAME, "DISFundStdPriceSO", "select",
                            "DISCondFuncDTO", "selectMeta"),
    # 펀드별 보수비용비교: 합성총보수(TER) 등 (published monthly)
    "fees": ServiceSpec(APP_NAME, "DISFundFeeCmsSO", "select",
                        "DISCondFuncDTO", "selectMeta"),
}


def date_params(yyyymmdd: str, company_code: str = "") -> dict:
    """Build the DISCondFuncDTO params: tmpV30=date, tmpV11=company ('' = all)."""
    return {"tmpV30": yyyymmdd, "tmpV11": company_code}


# --- Positional column maps (tmpVN) ------------------------------------------
# field name -> response column tag. Confirmed against live rows + DISComOutputMetaSO.

# 펀드기준가격 (DISFundStdPriceSO) row:
#   tmpV1 운용사 | tmpV2 펀드명 | tmpV3 펀드유형 | tmpV4 설정일
#   tmpV5 설정원본(백만원) | tmpV6 기준가격(원) | tmpV9 순자산(백만원)
#   tmpV12 표준코드 | tmpV13 회사코드 | tmpV14 기준일자
STDPRICE_COLUMNS = {
    "fund_code": "tmpV12",
    "fund_name": "tmpV2",
    "manager": "tmpV1",
    "fund_type": "tmpV3",
    "base_date": "tmpV14",
    "nav": "tmpV6",                 # 기준가격 (원)
    "aum_settlement": "tmpV5",      # 설정원본/설정액 (백만원)
    "net_assets": "tmpV9",          # 순자산총액 (백만원)
}

# 펀드별 보수비용비교 (DISFundFeeCmsSO) row (values are %):
#   tmpV1 운용사 | tmpV2 펀드명 | tmpV3 유형 | tmpV4 설정일
#   tmpV5 운용보수 | tmpV6 판매보수 | tmpV7 수탁보수 | tmpV8 사무관리보수
#   tmpV9 보수합계(A) | tmpV12 TER(A+B, 합성총보수) | tmpV15 표준코드
FEE_COLUMNS = {
    "fund_code": "tmpV15",
    "ter_synthetic": "tmpV12",      # TER (A+B) = 합성 총보수·비용비율
    "mgmt_fee": "tmpV5",            # 운용보수
    "sales_fee": "tmpV6",          # 판매보수
    # base_date is NOT in the fee row -> injected from the query date.
}

# Keywords used to identify a TDF among all funds (case-insensitive).
TDF_NAME_KEYWORDS = ("TDF", "TARGET DATE", "타겟데이트", "타깃데이트")
