# 문서 인덱스 (TDF 크롤러)

이 폴더는 **역할(페르소나)별** 로 나뉘어 있습니다. 본인 역할 문서부터 읽으세요.
프로젝트 전반 개요는 루트 [README.md](../README.md), 데이터 의미는 [DATA.md](../DATA.md) 참고.

| 페르소나 | 폴더 | 무엇을 보는가 |
|---|---|---|
| 🏛 **설계자(Architect)** | [architect/](architect/README.md) | 현재 범위(한국 TDF), 설계 원칙·결정, 향후 확장(엣지케이스)·스키마 진화 전략 |
| 🛠 **개발자(Developer)** | [developer/](developer/README.md) | 코드 구조, KOFIA API 변경 대응, 크롤링 실패 모드 예측·대응, 모니터링 훅, 테스트/픽스처 |
| 🚀 **운영자(Operator)** | [operator/](operator/README.md) | cron 배치 운영, 로그, **서버 중단 시 데이터 복구**, 백업 |
| 📊 **분석가(Analyst)** | [analyst/](analyst/README.md) | 스키마/조인, 단위·주의점, 분석 쿼리 레시피, 데이터 품질 체크, 분석팀 구성 |
| 🗂 **공통 — DB 스키마** | [schema/](schema/README.md) | **ER 다이어그램 + 컬럼별 데이터 사전**(타입·단위·원천·예시) |
| 🚀 **운영 배포(표준)** | [DEPLOY.md](DEPLOY.md) | ssh-keygen → `git clone` → venv → cron (GCP VM 리눅스). 도커 등 옛 옵션은 `legacy/` |
| 🎓 **입문자 학습** | [../team_learning/](../team_learning/README.md) | 파이썬 기초만 아는 팀원이 크롤러를 단계별로 직접 만들며 배우는 과정 |

## 한 장 요약 (TL;DR)

- **무엇**: 국내 Target Date Fund(TDF)의 일별 **기준가·설정액·순자산·자금흐름**과 월별 **합성총보수(TER)** 를
  KOFIA 전자공시(`dis.kofia.or.kr`)에서 수집해 **SQLite**(`data/tdf.db`)에 시계열로 누적.
- **어떻게 쌓이나**: 매일 그날 전체 TDF 스냅샷 1장을 적재(증분 컬럼 갱신이 아님). PK `(fund_code, base_date)` +
  멱등 upsert → 재실행/중복 안전. 과거 전체는 `backfill`로 누적.
- **어떻게 실행**: GCP VM에 `git clone` → venv → **매일 08:00 KST cron**. (표준: [DEPLOY.md](DEPLOY.md))
- **무엇이 변하기 쉬운가**: KOFIA 서비스ID·컬럼 위치·게이트웨이 URL → 전부 `tdf_crawler/config.py` 한 곳에 격리.

## 역할 간 협업 인터페이스 (요약)

```
설계자 ──(데이터 모델/확장 계약: models.py·스키마)──▶ 개발자
개발자 ──(config 계약·crawl_runs 관측치·알림)──▶ 운영자
운영자 ──(적재된 read-only DB/복제본)──▶ 분석가
분석가 ──(요구 지표·데이터 품질 이슈 피드백)──▶ 설계자
```

각 경계에서 "무엇이 바뀌면 누구에게 알려야 하는가"는 해당 페르소나 문서의 *협업/소통* 절 참고.
