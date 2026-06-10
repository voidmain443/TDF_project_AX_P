# 🚀 운영자(Operator) 문서

> 대상: 크론 배치를 관리하고, 서버가 죽었을 때 데이터를 복구하고, 적재 상태를 모니터링하는 사람.

> ⚠️ **배포 표준은 [docs/DEPLOY.md](../DEPLOY.md)** (GCP VM · `git clone` · venv · cron). 이 문서의
> **복구·백업·모니터링·트러블슈팅은 그대로 유효**합니다. 단, 아래 일부 절의 `docker compose …` 예시는
> **옛 Docker 방식([legacy/](../../legacy/README.md))** 기준이라, venv 환경에선 다음으로 바꿔 읽으세요:
> `docker compose run --rm crawler X` → `cd ~/tdf-crawler && .venv/bin/python -m tdf_crawler.X` ·
> `…shell sqlite3 /data/tdf.db` → `.venv/bin/python`으로 `data/tdf.db` 조회.

## 0. 한눈에 (운영 모델)

- **표준 배포 = GCP VM `git clone` + venv + cron** ([DEPLOY.md](../DEPLOY.md)). (Docker는 legacy)
- **데이터 = 단일 SQLite 파일** `~/tdf-crawler/data/tdf.db`. VM 디스크에 보관 → 정기 백업 권장(5절).
- **스케줄 = 매일 08:00 KST** cron. 모든 적재는 **멱등** → 재실행/중복 안전.
- **상태 = `crawl_runs` 테이블** (실행마다 상태/건수/오류 기록). 헬스체크·복구의 1차 신호.

## 1. Docker 실행 (리눅스 서버)

```bash
# 1) 이미지 빌드
docker compose build

# 2) 상시 스케줄러 가동 (매일 08:00 KST 자동 적재)
docker compose up -d crawler
docker compose logs -f crawler          # 동작 로그

# 3) 수동/배치 실행 (one-shot, 끝나면 컨테이너 제거)
docker compose run --rm crawler daily                       # 오늘자
docker compose run --rm crawler daily --date 2026-06-04     # 특정일
docker compose run --rm crawler backfill --start 2024-01-01 # 과거 전체 누적
docker compose run --rm crawler shell sqlite3 /data/tdf.db  # DB 직접 조회
```

`docker compose` 없이 순수 docker로도 동일:
```bash
docker build -f docker/Dockerfile -t tdf-crawler .
docker run -d --name tdf -e TZ=Asia/Seoul -v "$PWD/data:/data" tdf-crawler        # 스케줄러
docker run --rm -v "$PWD/data:/data" tdf-crawler daily                            # 단발
```

### 환경변수
| 변수 | 기본 | 용도 |
|---|---|---|
| `TDF_DB_PATH` | `/data/tdf.db` | DB 파일 경로(반드시 마운트된 볼륨 안) |
| `TZ` | `Asia/Seoul` | 컨테이너 시간대(크론 발화 시각 기준) |
| `TDF_XML_GATEWAY` | (config 기본) | KOFIA 게이트웨이 URL 교체(구조 변경 시 코드 수정 없이) |

## 2. 스케줄 운영 옵션

1. **컨테이너 내부 cron** (기본, `docker compose up -d crawler`): `docker/crontab` 의 `0 8 * * *`.
   시각 변경 → `docker/crontab` 수정 후 `docker compose build && docker compose up -d`.
2. **호스트 cron으로 one-shot 호출**(상시 컨테이너 싫을 때):
   ```cron
   0 8 * * *  cd /opt/tdf-crawler && docker compose run --rm crawler daily >> /var/log/tdf.log 2>&1
   ```
3. **Kubernetes CronJob**: 이미지 그대로, `args: ["daily"]`, PVC를 `/data`에 마운트.

> 첫 배포 시 과거 데이터는 `backfill`로 1회 채우고, 이후 매일 cron이 증분(그날 스냅샷)을 더합니다.

## 3. 로그 & 모니터링

- **로그 위치**: `/data/logs/crawl_YYYY-MM-DD.log` (호스트 `./data/logs/...`).
- **최근 실행 상태**(헬스의 핵심):
  ```bash
  docker compose run --rm crawler shell sqlite3 /data/tdf.db \
    "SELECT run_id,run_date,status,records_upserted,finished_at FROM crawl_runs ORDER BY run_id DESC LIMIT 10"
  ```
- **compose healthcheck**: 마지막 run이 `error`면 컨테이너 unhealthy(`docker ps`의 STATUS). 알림 연동 지점.
- **권장 경보**: ① 최근 run `status=error` ② 당일 `nav` 행수 급감(<1000=구조변경 의심) ③ 24h 내 성공 run 없음.

## 4. ⭐ 서버 중단 시 데이터 복구 (핵심 운영 절차)

### 왜 대부분 안전한가
- SQLite는 **WAL 모드**, 피드별 commit, **멱등 upsert**(PK=`fund_code,base_date`).
  → 적재 도중 컨테이너/호스트가 죽어도 **DB 손상 없이** "그 시점까지 커밋된 데이터"는 남고,
  **해당 날짜를 다시 실행하면 중복 없이 동일 상태로 수렴**합니다.

### 시나리오별 복구
| 상황 | 조치 |
|---|---|
| 적재 중 컨테이너 강제종료 | 그냥 다시 실행: `docker compose run --rm crawler daily --date <그날>` (멱등) |
| 며칠간 서버 정지(크론 누락) | 누락 구간 백필: `docker compose run --rm crawler backfill --start <첫누락일>` (resume로 빈 날만 채움) |
| DB 파일은 살아있음 | 무조치. 다음 cron이 이어서 진행 |
| 볼륨/디스크 유실 | 백업에서 복원(5절) 후, 백업 이후 구간 `backfill` |

### 누락 날짜 식별 쿼리
```sql
-- 성공 적재된 날짜 목록(역순) — 빠진 영업일을 눈으로/스크립트로 확인
SELECT DISTINCT base_date FROM nav_daily ORDER BY base_date DESC LIMIT 30;
-- 실패로 끝난 실행
SELECT run_id, run_date, error FROM crawl_runs WHERE status='error' ORDER BY run_id DESC;
```
빠진 구간을 찾으면 `backfill --start <시작> --end <끝>` (이미 있는 날은 자동 스킵).

### WAL 체크포인트(정상 종료 보장)
비정상 종료가 잦았다면 WAL을 본문에 합치고 무결성 점검:
```bash
docker compose run --rm crawler shell sqlite3 /data/tdf.db "PRAGMA wal_checkpoint(TRUNCATE); PRAGMA integrity_check;"
```
`integrity_check`가 `ok`가 아니면 6절 손상 복구.

## 5. 백업

SQLite 백업은 **온라인 백업 API**를 쓰는 게 안전(파일 복사 중 쓰기와 충돌 방지):
```bash
# 일관성 있는 스냅샷 백업 (실행 중에도 안전)
docker compose run --rm crawler shell \
  sqlite3 /data/tdf.db ".backup /data/backups/tdf-$(date +%F).db"
```
- 호스트 cron으로 매일 `.backup` → `./data/backups/` 보관(7~30일 롤링 권장).
- 또는 컨테이너 정지 후 `./data/tdf.db*` 파일 일괄 복사(스케줄러 멈춘 상태에서만).
- 오프사이트(S3 등)로 주기 업로드 권장. **백업 없이는 볼륨 유실 = 데이터 유실**.

## 6. 손상 복구 (최후수단)
```bash
# 손상 의심 시 덤프→재적재로 복구 시도
docker compose run --rm crawler shell bash -lc \
  "sqlite3 /data/tdf.db '.recover' | sqlite3 /data/tdf_recovered.db && mv /data/tdf_recovered.db /data/tdf.db"
```
복구 후 부족분은 `backfill`로 재수집(원천이 KOFIA이므로 언제든 재구축 가능 = 본 설계의 안전판).

## 7. 용량/유지보수
- 규모 감각: TDF ~1,950개 × 영업일 ≈ 연 ~50만 nav행. SQLite로 수년치 충분(수백 MB대).
- 트래픽: **영업일 1회 = 약 36MB 다운로드**. `backfill`은 (영업일 수 × 36MB)이므로 장기간은 `--delay`로 완급 조절.
- 디스크 풀 → 적재 실패. `./data` 디스크 여유·백업 롤링 정리.

## 8. Windows ↔ Docker(Linux) 차이 (운영자 주의)

| 항목 | Windows(로컬) | Docker(Linux, 표준) |
|---|---|---|
| 용도 | 개발·수동 점검 | **상시 운영/배치** |
| 실행 | `python -m tdf_crawler.run` / `scripts\run_daily.ps1` | `docker compose run --rm crawler daily` |
| 스케줄 | 작업 스케줄러(`register_task_windows.ps1`) | 컨테이너 cron / 호스트 cron / k8s CronJob |
| DB 경로 | `data\tdf.db`(프로젝트 폴더) | `/data/tdf.db`(마운트 볼륨) |
| 시간대 | OS 로컬 | `TZ=Asia/Seoul`(이미지 설정). **기준일 자체는 OS TZ 무관**(`today_kst`가 KST 계산) |
| 콘솔 인코딩 | cp949 → 한글 print 깨질 수 있음(`PYTHONUTF8=1` 권장) | UTF-8 기본, 문제 없음 |
| 줄바꿈 | CRLF | LF (`.sh`는 LF 유지 필수) |
| 권장 | 1회성/디버그 | **모두가 동일하게 돌리는 정식 경로** |

> 결론: **운영은 Docker로 통일**. 윈도우는 개발자가 빠르게 확인하는 보조 수단으로만 사용 권장.

## 9. 빠른 트러블슈팅 런북
| 증상 | 1차 확인 | 조치 |
|---|---|---|
| 당일 데이터 없음 | `crawl_runs` 최신 status | error면 로그 확인→개발자, empty면 휴장일 |
| 모든 날 0건 | 로그에 `<html` 에러페이지? | `TDF_XML_GATEWAY` 점검(개발자 문서 2a) |
| 컨테이너 unhealthy | 마지막 run error | 해당일 재실행, 반복되면 개발자 에스컬레이션 |
| 디스크 풀 | `df -h`, `./data` 용량 | 백업 정리/볼륨 확장 |
| 시각 안 맞음 | 컨테이너 `date` / `TZ` | `TZ=Asia/Seoul` 확인, crontab 시각 |
