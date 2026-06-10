# ☁️🚀 클라우드에서 1주일치 DB 구축 (운영 프로젝트, venv)

> 운영 프로젝트(`tdf_crawler`)를 **GCP VM에서** 돌려 **최근 약 1주일치** 데이터를 SQLite에 쌓는 실습.
> 표준 경로(ssh-keygen → git clone → venv → cron)의 전체는 [docs/DEPLOY.md](../docs/DEPLOY.md) 참고.
>
> ✅ **실제 검증됨**: GCP VM(Ubuntu, **venv**)에서 5영업일·nav 9,757행 적재 확인.
> `run_week.sh`/`verify.sh`는 환경을 자동 감지합니다(venv 우선).

## 0. 사전 (1회) — [docs/DEPLOY.md](../docs/DEPLOY.md) Step 1~3
```bash
ssh -i ~/.ssh/gcp_tdf <vm-user>@<vm-ip>                  # ssh-keygen 키로 접속
sudo apt update && sudo apt install -y git python3-venv python3-pip
git clone <your-repo> ~/tdf-crawler && cd ~/tdf-crawler
python3 -m venv .venv && .venv/bin/pip install -e .
```

## 1. 1주일치 빌드 + 검증 (스크립트 한 줄)
```bash
cd ~/tdf-crawler
bash cloud_quickstart/run_week.sh        # 최근 7일 적재 + 검증 (일수 조절: run_week.sh 10)
bash cloud_quickstart/verify.sh          # 언제든 상태 확인(행수·날짜·시계열)
```
스크립트가 하는 일(=직접 명령):
```bash
.venv/bin/python -m tdf_crawler.backfill --start <7일전> --delay 1   # 영업일만, 휴장일 스킵, resume
```

### 성공 예시 (실제)
```
1주일치 백필: 2026-06-03 → 오늘 (휴장일 자동 스킵)
[2/6] 2026-06-04 -> ok (nav=1950) ... [6/6] 2026-06-10 -> ok
적재된 날짜 수 : 5 / nav 총 행수 : 9757 / TDF 펀드 수 : 1953
```

## 2. 매일 자동 (cron)
```bash
sudo timedatectl set-timezone Asia/Seoul && mkdir -p logs
echo "0 8 * * * cd ~/tdf-crawler && ~/tdf-crawler/.venv/bin/python -m tdf_crawler.run >> ~/tdf-crawler/logs/crawl.log 2>&1" | crontab -
crontab -l
```
다음 날 `verify.sh`로 날짜가 하나 늘면 — 클라우드 일일 적재 완성. 🎉

## 트러블슈팅
| 증상 | 해결 |
|---|---|
| 며칠이 `empty`로 스킵 | 휴장일(정상). 평일인데 전부 0이면 [개발자 문서](../docs/developer/README.md) 2절 |
| 백필이 너무 김 | `run_week.sh 3`(3일)로 축소 또는 `--delay`↑ |
| `crontab -l`이 빔 | `echo "..." \| crontab -` 직접 설치(set -e+grep 함정) |

## 다음
- 운영 배포 표준: [docs/DEPLOY.md](../docs/DEPLOY.md)
- 운영·복구·백업: [운영자 문서](../docs/operator/README.md)
- 학습용(축소판)으로 같은 흐름: [team_learning](../team_learning/README.md)

> 참고: Docker·PuTTY·멀티옵션 등 옛 방식은 [`legacy/`](../legacy/README.md)로 분리(GitHub 미반영).
