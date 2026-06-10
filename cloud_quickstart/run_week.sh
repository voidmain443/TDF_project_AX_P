#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# 클라우드 VM에서 "최근 약 1주일치" TDF 데이터를 크롤링해 SQLite에 쌓고 검증한다.
#   사용:  bash cloud_quickstart/run_week.sh [일수]      (기본 7일)
#   실행환경: Docker 또는 venv 를 자동 감지 (Docker 없으면 .venv 사용)
#   전제:  docs/deploy 가이드대로 코드가 VM에 있고, Docker 또는 .venv 가 준비됨
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail
cd "$(dirname "$0")/.."                        # 프로젝트 루트로 이동

DAYS="${1:-7}"
START="$(date -d "${DAYS} days ago" +%F)"      # 리눅스(GNU date): 약 1주일 전

# ── 실행 환경 자동 감지 ──────────────────────────────────────────
if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1 && [ -f docker-compose.yml ]; then
  MODE=docker
elif [ -x .venv/bin/python ]; then
  MODE=venv
else
  echo "❌ 실행 환경이 없습니다. Docker를 설치하거나 .venv 를 준비하세요(README 0절/부록A)."
  exit 1
fi

echo "==============================================================="
echo "  1주일치 백필:  ${START}  →  오늘   (모드: ${MODE}, 휴장일 자동 스킵)"
echo "==============================================================="

# ── 크롤링 ───────────────────────────────────────────────────────
if [ "$MODE" = docker ]; then
  docker compose build
  docker compose run --rm crawler backfill --start "${START}" --delay 1
else
  .venv/bin/python -m tdf_crawler.backfill --start "${START}" --delay 1
fi

# ── 검증 ─────────────────────────────────────────────────────────
echo
bash "$(dirname "$0")/verify.sh"

echo
echo "✅ 1주일치 DB 구축 완료!"
if [ "$MODE" = docker ]; then
  echo "   매일 자동 적재:  docker compose up -d crawler"
else
  echo "   매일 자동 적재(cron):  crontab -e 에 아래 한 줄 추가"
  echo "   0 8 * * * cd $(pwd) && $(pwd)/.venv/bin/python -m tdf_crawler.run >> $(pwd)/logs/crawl_\$(date +\\%F).log 2>&1"
fi
