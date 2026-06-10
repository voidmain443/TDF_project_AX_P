"""레슨 04: 받은 XML에서 TDF 펀드의 코드/이름/기준가를 뽑아 출력.

실행:  python team_learning/04_parse_xml/parse_v2.py
"""
import sys
import requests
from xml.etree import ElementTree as ET

sys.stdout.reconfigure(encoding="utf-8")

URL = "https://dis.kofia.or.kr/proframeWeb/XMLSERVICES/"
DATE = "20260604"
BODY = f"""<?xml version="1.0" encoding="utf-8"?>
<message><proframeHeader><pfmAppName>FS-DIS2</pfmAppName>
<pfmSvcName>DISFundStdPriceSO</pfmSvcName><pfmFnName>select</pfmFnName></proframeHeader>
<systemHeader></systemHeader>
<DISCondFuncDTO><tmpV30>{DATE}</tmpV30><tmpV11></tmpV11></DISCondFuncDTO></message>"""
HEADERS = {"Content-Type": "application/xml; charset=UTF-8", "User-Agent": "Mozilla/5.0"}


def local_name(tag: str) -> str:
    # XML 태그에 가끔 붙는 네임스페이스({...})를 떼고 순수 이름만.
    return tag.rsplit("}", 1)[-1]


def main():
    # 1) 데이터 받기 (레슨 03과 동일)
    raw = requests.post(URL, data=BODY.encode("utf-8"), headers=HEADERS, timeout=60).content

    # 2) XML 파싱: <selectMeta> 한 덩어리를 펀드 한 개로 본다
    root = ET.fromstring(raw)
    funds = []
    for el in root.iter():
        if local_name(el.tag) != "selectMeta":
            continue
        # 그 안의 자식 태그들을 {태그이름: 값} dict로 모은다
        row = {local_name(c.tag): (c.text or "").strip() for c in el}
        funds.append(row)

    print(f"전체 펀드 수: {len(funds)}")

    # 3) "펀드명에 TDF 포함" 인 것만 거른다 (= 가장 단순한 TDF 탐색)
    tdf = [f for f in funds if "TDF" in f.get("tmpV2", "").upper()]
    print(f"그중 TDF: {len(tdf)}\n")

    # 4) 앞 5개만, 보기 좋게 출력
    print(f"{'펀드코드':14} {'기준가':>10}  펀드명")
    print("-" * 70)
    for f in tdf[:5]:
        code = f.get("tmpV12", "")
        name = f.get("tmpV2", "")
        nav = float(f.get("tmpV6") or 0)   # 문자열 → 숫자
        print(f"{code:14} {nav:>10}  {name[:40]}")


if __name__ == "__main__":
    main()
