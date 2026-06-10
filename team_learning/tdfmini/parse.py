"""파싱 — 응답 XML에서 TDF 펀드만 골라 dict 리스트로 (순수함수, 레슨 04)."""
from xml.etree import ElementTree as ET
from . import config


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]          # 네임스페이스 제거


def _num(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def parse_tdf(xml_bytes: bytes) -> list[dict]:
    """<selectMeta> 한 덩어리=펀드 1개. 이름에 TDF가 있는 것만 dict로."""
    root = ET.fromstring(xml_bytes)
    out = []
    for el in root.iter():
        if _local(el.tag) != "selectMeta":
            continue
        row = {_local(c.tag): (c.text or "").strip() for c in el}
        name = row.get(config.COL["name"], "")
        if not any(k in name.upper() for k in config.TDF_KEYWORDS):
            continue                       # = TDF 탐색
        d = row.get(config.COL["date"], "")
        iso = f"{d[0:4]}-{d[4:6]}-{d[6:8]}" if len(d) == 8 else None
        out.append({
            "code": row.get(config.COL["code"]),
            "date": iso,
            "name": name,
            "company": row.get(config.COL["company"]),
            "nav": _num(row.get(config.COL["nav"])),
            "aum": _num(row.get(config.COL["aum"])),
        })
    return out
