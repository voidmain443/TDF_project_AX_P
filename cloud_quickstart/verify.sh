#!/usr/bin/env bash
# 언제든 DB 상태를 점검한다 (행수·날짜·시계열 샘플). Docker/venv 자동 감지.
#   사용:  bash cloud_quickstart/verify.sh
set -euo pipefail
cd "$(dirname "$0")/.."

if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1 && [ -f docker-compose.yml ]; then
  echo "===== DB 검증 (Docker) ====="
  docker compose run --rm -T crawler shell sqlite3 /data/tdf.db "
.mode list
SELECT '적재된 날짜 수 : ' || COUNT(DISTINCT base_date) FROM nav_daily;
SELECT '날짜 목록      : ' || GROUP_CONCAT(d, ' ') FROM (SELECT DISTINCT base_date d FROM nav_daily ORDER BY d);
SELECT 'nav 총 행수    : ' || COUNT(*) FROM nav_daily;
SELECT 'TDF 펀드 수    : ' || COUNT(*) FROM funds;
SELECT '최근 실행      : ' || run_date || ' (' || status || ')' FROM crawl_runs ORDER BY run_id DESC LIMIT 3;
"
elif [ -x .venv/bin/python ]; then
  echo "===== DB 검증 (venv) ====="
  .venv/bin/python - <<'PY'
import sqlite3
from tdf_crawler import config
db = str(config.DEFAULT_DB_PATH)
c = sqlite3.connect(db)
print("DB 위치        :", db)
print("적재된 날짜 수 :", c.execute("SELECT COUNT(DISTINCT base_date) FROM nav_daily").fetchone()[0])
dates = [r[0] for r in c.execute("SELECT DISTINCT base_date FROM nav_daily ORDER BY base_date")]
print("날짜 목록      :", " ".join(dates))
print("nav 총 행수    :", c.execute("SELECT COUNT(*) FROM nav_daily").fetchone()[0])
print("TDF 펀드 수    :", c.execute("SELECT COUNT(*) FROM funds").fetchone()[0])
row = c.execute("SELECT fund_code, fund_name FROM funds WHERE fund_name LIKE '%TDF2045%' LIMIT 1").fetchone()
if row:
    print(f"\n[샘플] {row[0]}  {row[1][:40]}")
    print("  날짜        기준가     설정액(백만)  순유입")
    for r in c.execute("""SELECT n.base_date, n.nav, n.aum_settlement, f.net_flow
        FROM nav_daily n LEFT JOIN flows_daily f
          ON f.fund_code=n.fund_code AND f.base_date=n.base_date
        WHERE n.fund_code=? ORDER BY n.base_date""", (row[0],)):
        nf = "" if r[3] is None else r[3]
        print(f"  {r[0]}  {r[1]:>9}  {r[2]:>10}  {nf}")
PY
else
  echo "❌ Docker도 venv도 없습니다."
  exit 1
fi
