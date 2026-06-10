"""받기 — KOFIA에 POST해서 응답 bytes를 돌려준다 (레슨 03의 그 요청)."""
import requests
from . import config


def fetch(date: str, company: str = "") -> bytes:
    """date=YYYYMMDD, company=운용사코드(빈값=전체). 응답 XML(bytes)."""
    body = f"""<?xml version="1.0" encoding="utf-8"?>
<message><proframeHeader><pfmAppName>FS-DIS2</pfmAppName>
<pfmSvcName>DISFundStdPriceSO</pfmSvcName><pfmFnName>select</pfmFnName></proframeHeader>
<systemHeader></systemHeader>
<DISCondFuncDTO><tmpV30>{date}</tmpV30><tmpV11>{company}</tmpV11></DISCondFuncDTO></message>"""
    r = requests.post(config.URL, data=body.encode("utf-8"), headers=config.HEADERS, timeout=60)
    r.raise_for_status()
    return r.content
