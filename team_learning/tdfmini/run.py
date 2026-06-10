"""지휘자 — 받기→파싱→저장을 엮는다 + CLI (레슨 06의 main이 여기로).

실행:  cd team_learning  &&  python -m tdfmini.run --company A01015 --date 20260610
"""
import argparse
import sys
from . import fetch, parse, store, config

try:                                        # 윈도우 콘솔 한글 깨짐 방지
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def ingest(date: str, company: str = "") -> tuple[int, int]:
    """한 번 실행 = 그날 스냅샷 1장. (수집건수, DB총행수) 반환."""
    raw = fetch.fetch(date, company)        # 받기
    rows = parse.parse_tdf(raw)             # 파싱(TDF만)
    con = store.connect()
    store.save(con, rows)                   # 저장(멱등)
    total = con.execute("SELECT COUNT(*) FROM tdf_nav").fetchone()[0]
    con.close()
    return len(rows), total


def main():
    ap = argparse.ArgumentParser(description="tdfmini — 학습용 TDF 크롤러")
    ap.add_argument("--date", default="20260610", help="기준일 YYYYMMDD(최근 평일)")
    ap.add_argument("--company", default="A01015", help="운용사코드(A01015=교보악사, 빈값=전체)")
    a = ap.parse_args()
    got, total = ingest(a.date, a.company)
    print(f"수집 {got}건 → tdf_nav 총 {total}행")
    print(f"DB: {config.DB}")
    print("👉 한 번 더 실행해도 행수가 그대로면 '멱등' 성공!")


if __name__ == "__main__":
    main()
