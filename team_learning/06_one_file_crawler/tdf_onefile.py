"""레슨 06: 한 파일로 동작하는 TDF 크롤러 (MVP).

받기 → 파싱 → TDF 거르기 → SQLite 저장(멱등). 두 번 실행해도 중복이 안 쌓인다.

실행:  python team_learning/06_one_file_crawler/tdf_onefile.py
"""
import sys
import sqlite3
from pathlib import Path
import requests
from xml.etree import ElementTree as ET

sys.stdout.reconfigure(encoding="utf-8")

# ── 설정(나중에 config.py가 되는 부분) ──────────────────────────────
URL = "https://dis.kofia.or.kr/proframeWeb/XMLSERVICES/"
DATE = "20260604"                       # 최근 평일로 변경 가능
DB = Path(__file__).resolve().parent.parent / "playground.db"
HEADERS = {"Content-Type": "application/xml; charset=UTF-8", "User-Agent": "Mozilla/5.0"}
# tmpV 위치 → 의미 (이 '약속'을 한 곳에 모아두는 게 config의 핵심 아이디어)
COL = {"code": "tmpV12", "name": "tmpV2", "manager": "tmpV1", "nav": "tmpV6",
       "aum": "tmpV5", "date": "tmpV14"}


# ── 받기(나중에 fetchers/) ─────────────────────────────────────────
def fetch(date: str) -> bytes:
    body = f"""<?xml version="1.0" encoding="utf-8"?>
<message><proframeHeader><pfmAppName>FS-DIS2</pfmAppName>
<pfmSvcName>DISFundStdPriceSO</pfmSvcName><pfmFnName>select</pfmFnName></proframeHeader>
<systemHeader></systemHeader>
<DISCondFuncDTO><tmpV30>{date}</tmpV30><tmpV11></tmpV11></DISCondFuncDTO></message>"""
    return requests.post(URL, data=body.encode("utf-8"), headers=HEADERS, timeout=60).content


# ── 파싱(나중에 parsers.py) ────────────────────────────────────────
def _local(tag): return tag.rsplit("}", 1)[-1]

def _num(s):
    try: return float(s)
    except (TypeError, ValueError): return None

def parse_tdf(raw: bytes) -> list[dict]:
    root = ET.fromstring(raw)
    out = []
    for el in root.iter():
        if _local(el.tag) != "selectMeta":
            continue
        r = {_local(c.tag): (c.text or "").strip() for c in el}
        name = r.get(COL["name"], "")
        if "TDF" not in name.upper():          # ← TDF 거르기(나중에 discovery.py)
            continue
        d = r.get(COL["date"], "")             # '20260604' → '2026-06-04'
        iso = f"{d[0:4]}-{d[4:6]}-{d[6:8]}" if len(d) == 8 else None
        out.append({
            "code": r.get(COL["code"]), "name": name, "manager": r.get(COL["manager"]),
            "date": iso, "nav": _num(r.get(COL["nav"])), "aum": _num(r.get(COL["aum"])),
        })
    return out


# ── 저장(나중에 db.py): PRIMARY KEY + upsert = 멱등 ────────────────
def save(rows: list[dict]) -> None:
    con = sqlite3.connect(DB)
    con.execute("""
        CREATE TABLE IF NOT EXISTS tdf_nav (
            fund_code TEXT,
            base_date TEXT,
            fund_name TEXT,
            manager   TEXT,
            nav       REAL,
            aum       REAL,
            PRIMARY KEY (fund_code, base_date)   -- 한 펀드 × 한 날짜 = 한 행
        )
    """)
    con.executemany("""
        INSERT INTO tdf_nav (fund_code, base_date, fund_name, manager, nav, aum)
        VALUES (:code, :date, :name, :manager, :nav, :aum)
        ON CONFLICT(fund_code, base_date) DO UPDATE SET   -- 이미 있으면 덮어쓰기
            fund_name=excluded.fund_name, manager=excluded.manager,
            nav=excluded.nav, aum=excluded.aum
    """, [r for r in rows if r["code"] and r["date"]])
    con.commit()
    con.close()


# ── 흐름(나중에 run.py) ────────────────────────────────────────────
def main():
    print(f"1) 받기   : {DATE}")
    raw = fetch(DATE)
    print(f"2) 파싱   : ", end="")
    rows = parse_tdf(raw)
    print(f"TDF {len(rows)}건")
    print("3) 저장   : (멱등 upsert)")
    save(rows)

    con = sqlite3.connect(DB)
    total = con.execute("SELECT COUNT(*) FROM tdf_nav").fetchone()[0]
    dates = con.execute("SELECT COUNT(DISTINCT base_date) FROM tdf_nav").fetchone()[0]
    print(f"\n✅ tdf_nav 총 {total}행 (날짜 {dates}개) — DB: {DB}")
    print("   👉 이 스크립트를 한 번 더 실행해도 행 수가 그대로면 '멱등' 성공!")
    con.close()


if __name__ == "__main__":
    main()
