"""과거 누적 — 영업일을 돌며 며칠치를 쌓는다 (레슨 09).

실행:  cd team_learning  &&  python -m tdfmini.backfill 2026-06-04 2026-06-10
"""
import sys
from datetime import date, timedelta
from . import run

try:                                        # 윈도우 콘솔 한글 깨짐 방지
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def business_days(start: str, end: str) -> list[str]:
    """ISO 'YYYY-MM-DD' 범위의 평일(월~금) 목록."""
    d, last = date.fromisoformat(start), date.fromisoformat(end)
    out = []
    while d <= last:
        if d.weekday() < 5:
            out.append(d.isoformat())
        d += timedelta(days=1)
    return out


def backfill(start: str, end: str, company: str = "A01015") -> None:
    for iso in business_days(start, end):
        got, total = run.ingest(iso.replace("-", ""), company)   # YYYYMMDD
        mark = "" if got else "  (휴장일?)"
        print(f"{iso}: {got}건{mark}")
    print("→ 멱등이라 다시 돌려도 중복 안 쌓임. 이미 받은 날도 안전.")


if __name__ == "__main__":
    s = sys.argv[1]
    e = sys.argv[2] if len(sys.argv) > 2 else s
    backfill(s, e)
