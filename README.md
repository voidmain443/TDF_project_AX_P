# TDF Daily Crawler (KOFIA → SQLite)

국내 **Target Date Fund(TDF)** 의 매일 **기준가 · 설정액 · 자금 유출입 · 합성 총보수**를
한국금융투자협회(KOFIA) 펀드공시(`dis.kofia.or.kr`)에서 수집해 워크스페이스 내 SQLite DB에
적재합니다. 모든 적재는 멱등(upsert) 이라 매일/재실행해도 중복이 쌓이지 않습니다.

## 🧭 이 워크스페이스의 3가지 파트

| 파트 | 폴더 | 무엇 | 배포 |
|---|---|---|---|
| **① 운영 프로젝트** | `tdf_crawler/` · `data/` · `docs/` | 실제 크롤러 + 실데이터(과거+매일) + 역할별 문서 | GitHub → GCP VM `git clone` → 리눅스 [DEPLOY.md](docs/DEPLOY.md) |
| **② 학습 파트** | `team_learning/` (+ `tdfmini/`) | 크롤링을 단계별로 직접 만드는 교육. **07부터 자체 코드 `tdfmini/`** | 학습 샌드박스 VM에 **ssh-keygen** 접속 |
| **③ 레거시** | `legacy/` | 도커·멀티옵션·PuTTY 등 옛 클라우드 문서 | **GitHub 미반영(.gitignore)** |

## 📚 문서 (역할별)

| 보는 사람 | 문서 |
|---|---|
| 데이터 의미·단위·누적 방식 | [DATA.md](DATA.md) |
| 🗂 DB 스키마 — ER 다이어그램·데이터 사전 | [docs/schema](docs/schema/README.md) |
| 🏛 설계자 — 범위·확장 전략 | [docs/architect](docs/architect/README.md) |
| 🛠 개발자 — 코드·API변경·실패대응 | [docs/developer](docs/developer/README.md) |
| 🚀 운영자 — cron·로그·**복구**·백업 | [docs/operator](docs/operator/README.md) |
| 📊 분석가 — 쿼리·품질·팀구성 | [docs/analyst](docs/analyst/README.md) |
| 🚀 **운영 배포(표준)** | [docs/DEPLOY.md](docs/DEPLOY.md) · [cloud_quickstart/](cloud_quickstart/README.md) |
| 🎓 **파이썬 기초만 아는 팀원용 학습** | [team_learning/](team_learning/README.md) |

문서 인덱스: [docs/README.md](docs/README.md)

## 구조

```
tdf_crawler/          # ① 운영 크롤러 (config·db·parsers·run·backfill·fetchers/ …)
data/                 # ① 실데이터 SQLite (gitignore)
docs/                 # ① 역할별 문서 + DEPLOY.md(배포 표준)
cloud_quickstart/     # ① VM 1주일 빌드 헬퍼(venv)
tests/                # ① pytest (네트워크 없이 픽스처)
team_learning/        # ② 학습 (00~11) + tdfmini/(07 리팩터링 결과물, 학습 자체 코드)
legacy/               # ③ 옛 클라우드 문서(도커·PuTTY·멀티옵션) — GitHub 미반영
```

## 🚀 운영 배포 (GCP VM · git clone · venv · cron)

```bash
ssh -i ~/.ssh/gcp_tdf <vm-user>@<vm-ip>            # ssh-keygen 키로 접속
git clone <your-repo> ~/tdf-crawler && cd ~/tdf-crawler
python3 -m venv .venv && .venv/bin/pip install -e .
bash cloud_quickstart/run_week.sh                  # 1주일치 적재+검증
# 매일 cron: docs/DEPLOY.md 4절
```
전체 절차(키 생성·등록·cron)는 **[docs/DEPLOY.md](docs/DEPLOY.md)**. (도커 등 옛 옵션은 [legacy/](legacy/README.md))

## 설치

```powershell
pip install -e .            # 기본(requests만)
pip install -e ".[dev]"     # 테스트 도구(pytest, freezegun)
pip install -e ".[selenium]"  # Selenium 폴백/실엔드포인트 캡처 시
```

## 사용법

```powershell
# 오늘자(KST) 전체 TDF 수집·적재 (기본 data/tdf.db)
python -m tdf_crawler.run

# 옵션
python -m tdf_crawler.run --source http        # 기본: 직접 HTTP/XML
python -m tdf_crawler.run --source selenium     # 폴백: 브라우저 경유
python -m tdf_crawler.run --date 2026-06-04      # 특정일 백필
python -m tdf_crawler.run --db D:\tdf.db          # DB 경로 지정
python -m tdf_crawler.run --dry-run -v            # 적재 없이 건수만 확인
```

DB 확인:

```powershell
python -c "import sqlite3;[print(r) for r in sqlite3.connect('data/tdf.db').execute('SELECT * FROM nav_daily LIMIT 5')]"
```

## 과거 데이터 전체 누적 (백필)

매일 스냅샷을 시계열로 채워 **과거 전체**를 한 번에 쌓습니다. 영업일마다 기준가/설정액/순자산,
월말마다 보수를 받아 적재하며, **이미 쌓인 날짜는 건너뜁니다(resume 기본)** — 중단해도 재실행하면 이어서 진행됩니다.

```powershell
# 시작일 지정(종료일 미지정 시 오늘까지). 기간이 길수록 시간/트래픽이 큽니다(한 영업일 ≈ 36MB).
python -m tdf_crawler.backfill --start 2020-01-01
python -m tdf_crawler.backfill --start 2026-05-01 --end 2026-06-04
python -m tdf_crawler.backfill --start 2026-05-01 --no-fees --delay 2   # 보수 제외 / 호출 간격 2초
```

- 영업일(월~금)만 호출하고 휴장일은 빈 응답으로 자동 스킵됩니다.
- 자금흐름(net_flow)은 과거→현재 순서로 적재하며 **전일 대비 설정액 증감**으로 자동 산출됩니다.
- 중단 후 재개: 같은 명령을 다시 실행하면 됨(`--no-resume` 로 강제 재수집).

## 테스트 (TDD)

```powershell
python -m pytest            # 오프라인 단위·통합 테스트 (네트워크 불필요)
python -m pytest -m live    # 실 KOFIA 호출 스모크 테스트
```

## 데이터 모델 / 동작 방식

**[DATA.md](DATA.md)** 에 데이터 출처·수집 방식·**누적 방식(매일 하루치 스냅샷 시계열 누적)**·
테이블별 컬럼 사전이 정리되어 있습니다. 실제 KOFIA 라이브 수집으로 검증 완료
(1회 실행 시 TDF 약 1,950개 클래스 적재).

### 엔드포인트 재확정이 필요할 때 (KOFIA 구조 변경 시)

서비스ID·컬럼 위치는 `tdf_crawler/config.py` 한 곳에 모여 있습니다. KOFIA가 바꾸면:

```powershell
# 최근 영업일/월말로 실 응답을 다시 받아 픽스처 갱신
python -m tdf_crawler.capture --date 2026-06-04 --fee-date 2026-04-30
```

그 후 태그·컬럼이 달라졌으면 `config.py`의 `SERVICES`·`*_COLUMNS`만 수정합니다.
게이트웨이 URL이 바뀌면 코드 수정 없이 환경변수로 지정 가능:

```powershell
$env:TDF_XML_GATEWAY = "https://dis.kofia.or.kr/<실제경로>"
```

## 매일 자동 실행 (cron, 리눅스 VM)

운영 표준은 **GCP VM의 cron** 한 줄입니다(멱등이라 재실행·누락보충 안전):
```bash
echo "0 8 * * * cd ~/tdf-crawler && ~/tdf-crawler/.venv/bin/python -m tdf_crawler.run >> ~/tdf-crawler/logs/crawl.log 2>&1" | crontab -
```
전체 절차는 **[docs/DEPLOY.md](docs/DEPLOY.md)**. (Windows 작업스케줄러·systemd·도커 방식은 [legacy/](legacy/README.md)로 분리)

## SQLite 스키마

| 테이블 | 키 | 내용 |
|---|---|---|
| `funds` | `fund_code` | 펀드 메타(이름·운용사·유형·만기연도) |
| `nav_daily` | `(fund_code, base_date)` | 기준가(원)·설정액(백만원)·순자산(백만원) |
| `flows_daily` | `(fund_code, base_date)` | 순유입(설정액 Δ 파생, 백만원) |
| `fees` | `(fund_code, base_date)` | 합성총보수(TER)·운용·판매보수 (%) |
| `crawl_runs` | `run_id` | 실행 이력(상태·건수·오류) |

자세한 컬럼별 의미·단위·출처는 [DATA.md](DATA.md) 참조.
