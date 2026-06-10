"""레슨 05: 받기 → 파싱 → SQLite 저장 (가장 단순 버전, 아직 중복 방지는 없음).

실행:  python team_learning/05_save_sqlite/save_v3.py
결과:  team_learning/playground.db 에 nav 테이블 생성/적재
"""
import sys
import sqlite3
from pathlib import Path
import requests
from xml.etree import ElementTree as ET

sys.stdout.reconfigure(encoding="utf-8")

URL = "https://dis.kofia.or.kr/proframeWeb/XMLSERVICES/"
DATE = "20260604"
DB = Path(__file__).resolve().parent.parent / "playground.db"   # team_learning/playground.db
BODY = f"""<?xml version="1.0" encoding="utf-8"?>
<message><proframeHeader><pfmAppName>FS-DIS2</pfmAppName>
<pfmSvcName>DISFundStdPriceSO</pfmSvcName><pfmFnName>select</pfmFnName></proframeHeader>
<systemHeader></systemHeader>
<DISCondFuncDTO><tmpV30>{DATE}</tmpV30><tmpV11></tmpV11></DISCondFuncDTO></message>"""
HEADERS = {"Content-Type": "application/xml; charset=UTF-8", "User-Agent": "Mozilla/5.0"}


def local(tag):
    return tag.rsplit("}", 1)[-1]


def fetch_and_parse():
    raw = requests.post(URL, data=BODY.encode("utf-8"), headers=HEADERS, timeout=60).content
    root = ET.fromstring(raw)
    rows = []
    for el in root.iter():
        if local(el.tag) != "selectMeta":
            continue
        r = {local(c.tag): (c.text or "").strip() for c in el}
        if "TDF" not in r.get("tmpV2", "").upper():
            continue   # TDF만
        rows.append((
            r.get("tmpV12"),                 # 펀드코드
            DATE,                            # 날짜
            float(r["tmpV6"]) if r.get("tmpV6") else None,  # 기준가
            r.get("tmpV2"),                  # 펀드명
        ))
    return rows


def main():
    rows = fetch_and_parse()
    print(f"파싱된 TDF 행: {len(rows)}")

    con = sqlite3.connect(DB)
    # 표 만들기 (없으면)
    con.execute("""
        CREATE TABLE IF NOT EXISTS nav (
            fund_code TEXT,
            base_date TEXT,
            nav       REAL,
            fund_name TEXT
        )
    """)
    # 행 넣기 — ? 자리표시자로 안전하게
    con.executemany("INSERT INTO nav VALUES (?, ?, ?, ?)", rows)
    con.commit()

    total = con.execute("SELECT COUNT(*) FROM nav").fetchone()[0]
    print(f"저장 완료! 현재 nav 테이블 총 행 수: {total}")
    print(f"DB 파일: {DB}")
    print("\n⚠️  이 스크립트를 또 실행하면 같은 데이터가 '중복'으로 쌓입니다.")
    print("    → 레슨 06에서 PRIMARY KEY + upsert로 해결합니다.")
    con.close()


if __name__ == "__main__":
    main()
