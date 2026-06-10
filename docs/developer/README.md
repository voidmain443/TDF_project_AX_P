# 🛠 개발자(Developer) 문서

> 대상: 크롤러를 유지보수하고, KOFIA가 바뀌거나 수집이 깨질 때 진단·수정하며, 운영에서 생길 문제를 미리 막는 사람.

## 1. 코드 구조 & 데이터 흐름

```
fetch (네트워크)        parse (순수)            store (멱등)
─────────────────       ──────────────         ─────────────────
fetchers/http_fetcher → parsers.map_*       → db.upsert_* / compute_flows
   │  build_envelope        │  selectMeta/tmpVN    │  ON CONFLICT
   ▼                        ▼                      ▼
config.SERVICES        models.dataclass       SQLite (data/tdf.db)
config.*_COLUMNS                              crawl_runs(관측)
```

| 모듈 | 책임 | 바뀔 일이 |
|---|---|---|
| `config.py` | 게이트웨이 URL, 서비스ID, `tmpVN` 컬럼맵, TDF 키워드 | **자주**(KOFIA 변경 시 여기만) |
| `fetchers/` | Proframe XML POST(http 기본 / selenium 폴백), 재시도 | 드묾 |
| `parsers.py` | XML→dataclass 순수 변환 | 컬럼 구조 변경 시 |
| `discovery.py` | 펀드명으로 TDF 판별 | 키워드 확장 시 |
| `collectors.py` | 일자별 fetch+parse 오케스트레이션, 보수 월말 백워크 | 드묾 |
| `db.py` | 스키마, upsert, 자금흐름 파생/재계산 | 스키마 확장 시 |
| `run.py` | 일일 ingest + CLI | 드묾 |
| `backfill.py` | 과거 누적(영업일/월말 반복, resume) | 드묾 |
| `capture.py` | 실응답 재캡처→픽스처 갱신 | 픽스처 갱신 시 |

## 2. KOFIA API/구조 변경 대응 (가장 중요한 운영 리스크)

KOFIA는 비공개 내부 API라 **사전 공지 없이** 바뀔 수 있습니다. 변경 유형별 대응:

### (a) 게이트웨이 URL 변경 → 증상: 전부 0건 / 307 / HTML 에러페이지
- 과거 실제 사례: `proframeweb`(소문자)는 죽은 레거시라 307→에러. 정답은 `proframe**W**eb`(대문자 W).
- **대응**: 코드 수정 없이 `TDF_XML_GATEWAY` 환경변수로 교체. 새 경로는 브라우저 Network 탭에서 확인.

### (b) 서비스ID(`pfmSvcName`) 변경 → 증상: 특정 피드만 0건/에러
- **대응**: 브라우저로 해당 공시 화면을 열고 XHR의 `pfmSvcName` 확인 → `config.SERVICES` 수정.
- 메뉴 전체 경로는 `DISMenuSO` 응답(페이지별 serviceId 포함)에서 일괄 확인 가능.

### (c) 응답 컬럼 위치(`tmpVN`) 변경 → 증상: 적재는 되나 값이 NULL/엉뚱
- **대응**: `DISComOutputMetaSO`(헤더 라벨 서비스)로 라벨↔컬럼 재매핑 → `config.*_COLUMNS` 수정.
- 검증: `python -m tdf_crawler.capture --date <영업일> --fee-date <월말>` 후 `pytest`(픽스처 자동 반영).

### (d) 행 래퍼(`selectMeta`) 변경 → 증상: 행 0개로 파싱
- **대응**: 실응답에서 반복 요소명 확인 → `ServiceSpec.row_tag` 수정.

> 황금률: **변경은 거의 항상 `config.py` 한 곳**에서 끝납니다. 그게 본 설계의 목적.

### 변경 감지 자동화(권장 구현)
- 일일 실행 후 `nav` 행수가 임계치(예: <1000) 미만이면 알림 → 구조 변경 조기 경보.
- `crawl_runs.status='error'` 또는 `records_upserted` 급감 모니터(운영 문서의 헬스체크와 연계).

## 3. 크롤링 실패 모드 & 예측적 대응

| 증상 | 가능 원인 | 진단 | 대응 |
|---|---|---|---|
| 전부 0건 | 게이트웨이 URL/세션 | 응답 앞부분이 `<html` 에러페이지인지 | (a) 항목, `TDF_XML_GATEWAY` |
| 특정일만 0건 | **휴장일**(정상) vs 구조변경 | 인접 영업일도 0인지 | 휴장일이면 무시(`empty` 기록) |
| 값이 NULL/이상 | 컬럼 위치 변경 | 메타 라벨과 대조 | (c) 항목 |
| 보수 0건 | 아직 미공시(월 시차) | `fee_date` 로그 확인 | 정상. 다음달 자동 백워크 |
| 타임아웃 | 36MB 응답·네트워크 | `DEFAULT_TIMEOUT` | 타임아웃↑, 재시도(이미 3회) |
| 간헐 5xx/차단 | 레이트리밋 | 반복 실패 패턴 | `--delay`↑, Selenium 폴백 |
| 메모리 급증 | 26k행 36MB ElementTree | RSS 모니터 | 스트리밍 파서(iterparse) 전환 고려 |
| flows 비어있음 | 직전 영업일 데이터 없음 | nav 날짜 2개 이상인지 | 정상(첫날) / `recompute_all_flows` |

### 운영에서 생길 문제를 위한 사전 개발 포인트
- **부분 실패 안전**: 피드별 commit + 멱등 upsert → 중간에 죽어도 재실행 수렴(운영 복구와 직결).
- **resume**: `backfill`은 `crawl_runs` 기준으로 완료 날짜 스킵 → 장시간 작업 중단 내성.
- **휴장일 구분**: 0건 응답을 `empty`로 기록해 재시도 폭주 방지(재캡처 비용 절감).
- **알림 훅 자리**: `run.ingest`/`finish_run` 직후가 Slack/메일 훅을 붙일 지점.

## 4. 테스트 전략

```powershell
python -m pytest          # 오프라인(픽스처) 단위·통합 — 네트워크 불필요, 빠름
python -m pytest -m live  # 실 KOFIA 1회 스모크 — 엔드포인트 살아있는지
```

- **오프라인 우선**: 모든 로직은 `tests/fixtures/`의 실제 응답 트림본으로 검증. CI 친화.
- **픽스처 = 실데이터 트림**: `capture.py`가 실응답에서 TDF 몇 행만 잘라 생성(작게 유지).
- **라이브 마크**: `@pytest.mark.live`는 기본 제외(`addopts=-m 'not live'`). 엔드포인트 점검용.
- 변경 후 반드시: `capture` → `pytest`(오프라인) → `pytest -m live` 순으로 회귀 확인.

## 5. 디버깅 레시피

```powershell
# 적재 없이 건수만(엔드포인트/필터 확인)
python -m tdf_crawler.run --date 2026-06-04 --dry-run -v

# 특정 서비스 원응답 직접 확인(행 수/구조)
python -c "from tdf_crawler import config; from tdf_crawler.fetchers import HttpFetcher; import re; r=HttpFetcher().fetch(config.SERVICES['stdprice'], config.date_params('20260604')); print(len(r), len(re.findall(b'<selectMeta>', r)))"

# 마지막 실행 상태
python -c "import sqlite3;print(sqlite3.connect('data/tdf.db').execute('SELECT * FROM crawl_runs ORDER BY run_id DESC LIMIT 5').fetchall())"
```

## 6. 컨벤션
- 코어 의존성 추가 지양(이식성/Docker 경량). 무거운 건 `pyproject` extras로.
- 파서는 순수 유지(네트워크/DB 금지) → 테스트 가능성 보존.
- KOFIA 지식은 코드에 흩지 말고 `config.py`로.

## 7. 설계자·운영자와의 소통
- **설계자**: 새 피드/지표 요청 시 → 모델·테이블·단위 계약을 먼저 합의(설계자 문서 6절). 그 후 config+parser 구현.
- **운영자**: 알림 임계치·재시도/딜레이 기본값·로그 포맷은 운영 요구에 맞춰 노출(환경변수화 권장).
  구조 변경으로 0건이 나면 운영자가 가장 먼저 감지 → 개발자 에스컬레이션 경로를 운영 문서와 일치시킬 것.
