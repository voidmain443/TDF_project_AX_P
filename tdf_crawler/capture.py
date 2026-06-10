"""Re-capture real KOFIA responses as test fixtures.

Use this if KOFIA changes its service ids or column layout and the offline
tests need refreshing against reality. It calls the live services and trims the
bulk response down to a few TDF rows (plus one non-TDF) so fixtures stay small.

    python -m tdf_crawler.capture --date 2026-06-04 --fee-date 2026-04-30

To rediscover service ids / the tmpVN column layout from scratch (e.g. KOFIA
restructures a page), drive the page in a browser and watch the Network tab, or
see the XHR-sniffing approach documented in DATA.md.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from . import config
from .fetchers import get_fetcher

FIXTURES = Path(__file__).resolve().parent.parent / "tests" / "fixtures"
_HEAD = ('<?xml version="1.0" encoding="UTF-8"?><root><message>'
         '<proframeHeader><pfmSvcName>{svc}</pfmSvcName></proframeHeader>'
         '<systemHeader></systemHeader><DISCondFuncListDTO>'
         '<dbio_total_count_>{n}</dbio_total_count_>')


def _trim(raw: bytes, svc: str, name_col: str, keep_tdf: int, keep_other: int) -> bytes:
    text = raw.decode("utf-8", "ignore")
    rows = re.findall(r"<selectMeta>.*?</selectMeta>", text, re.S)

    def is_tdf(r: str) -> bool:
        m = re.search(rf"<{name_col}>([^<]*)</{name_col}>", r)
        nm = (m.group(1) if m else "").upper()
        return any(k.upper() in nm for k in config.TDF_NAME_KEYWORDS)

    tdf = [r for r in rows if is_tdf(r)]
    other = [r for r in rows if not is_tdf(r)]
    sel = tdf[:keep_tdf] + other[:keep_other]
    body = _HEAD.format(svc=svc, n=len(rows)) + "".join(s.strip() for s in sel)
    return (body + "</DISCondFuncListDTO></message></root>").encode("utf-8")


def capture(date: str, fee_date: str, source: str = "http") -> None:
    fetcher = get_fetcher(source)
    try:
        ymd = date.replace("-", "")
        sp = config.SERVICES["stdprice"]
        raw = fetcher.fetch(sp, config.date_params(ymd))
        (FIXTURES / "stdprice_sample.xml").write_bytes(
            _trim(raw, sp.service_name, config.STDPRICE_COLUMNS["fund_name"], 3, 1))
        print("wrote stdprice_sample.xml")

        fy = fee_date.replace("-", "")
        fe = config.SERVICES["fees"]
        raw = fetcher.fetch(fe, config.date_params(fy))
        (FIXTURES / "fee_sample.xml").write_bytes(
            _trim(raw, fe.service_name, "tmpV2", 3, 1))
        print("wrote fee_sample.xml")
    finally:
        close = getattr(fetcher, "close", None)
        if callable(close):
            close()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Re-capture KOFIA fixtures.")
    p.add_argument("--date", required=True, help="business date YYYY-MM-DD for 기준가")
    p.add_argument("--fee-date", required=True, help="month-end YYYY-MM-DD for 보수")
    p.add_argument("--source", choices=["http", "selenium"], default="http")
    args = p.parse_args(argv)
    capture(args.date, args.fee_date, args.source)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
