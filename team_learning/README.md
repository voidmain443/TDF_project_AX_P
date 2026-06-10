# 🎓 team_learning — "크롤러를 직접 만들며 배우기"

> 대상: **파이썬 기초 문법만** 아는 팀원. 크롤링이 처음이어도 괜찮습니다.
> 목표: 이 프로젝트(`tdf_crawler`)가 **어떻게 한 단계씩 만들어졌는지**를 직접 따라 만들며 이해하기.

## 이 학습의 철학 — "전통적인 방식: 작게 → 동작 → 정리"

처음부터 멋진 폴더 구조를 만들지 않습니다. 실제 개발이 그렇듯:

```
[Part 1: 로컬에서 만들고 이해]
한 줄 요청 → 응답 출력 → 파싱 → 저장 → "한 파일 크롤러" 완성(MVP)
        → 코드가 커지자 비로소 config/parser/db로 "분리"
        → 테스트로 안전망 → 멱등·자동화·과거 누적
[Part 2: 클라우드로 옮겨 매일 돌리기]
        → 클라우드 VM에 DB 생성(크롤링↔sqlite 연결) → cron으로 매일 무인 수집
```

각 레슨은 **(1) 개념 설명 → (2) 직접 실행하는 작은 코드 → (3) 무엇을 배웠나 → (4) 실제 프로젝트의 어느 파일이 되었나** 순서입니다.

## 학습 순서 (한 폴더 = 한 레슨)

### Part 1 — 로컬에서 크롤러 만들고 이해하기
| # | 폴더 | 배우는 것 | 실행 코드 |
|---|---|---|---|
| 00 | [00_setup](00_setup/README.md) | 파이썬·가상환경·pip·requests 설치 | — |
| 01 | [01_http_basics](01_http_basics/README.md) | HTTP 요청/응답이란? `requests`로 GET | `example.py` |
| 02 | [02_inspect_site](02_inspect_site/README.md) | 사이트는 데이터를 어떻게 주나(개발자도구·XHR) | — |
| 03 | [03_first_crawl](03_first_crawl/README.md) | 실제 KOFIA에 POST해서 데이터 한 번 받기 | `crawl_v1.py` |
| 04 | [04_parse_xml](04_parse_xml/README.md) | 응답 XML에서 원하는 값 뽑기 | `parse_v2.py` |
| 05 | [05_save_sqlite](05_save_sqlite/README.md) | SQLite에 저장하기 | `save_v3.py` |
| 06 | [06_one_file_crawler](06_one_file_crawler/README.md) | **동작하는 한 파일 크롤러(MVP)** | `tdf_onefile.py` |
| 07 | [07_refactor](07_refactor/README.md) | 한 파일을 책임별로 쪼개기 → **결과물 [`tdfmini/`](tdfmini/)** | `tdfmini/*.py` |
| 08 | [08_tdd](08_tdd/README.md) | 테스트로 안전하게 — `tdfmini.parse` | `tdfmini/test_parse.py` |
| 09 | [09_idempotent_schedule](09_idempotent_schedule/README.md) | 멱등성·과거 누적 — `tdfmini.run`/`backfill` | `tdfmini/*` |

> 💡 **레슨 07부터는 학습 폴더 자체 코드 [`tdfmini/`](tdfmini/)** 로 진행합니다(6주차 한 파일을 쪼갠 결과물).
> 실제 운영 코드 `tdf_crawler/`와 같은 아이디어의 축소판이에요.

### Part 2 — 클라우드로 옮겨 매일 자동 수집 (☁️ **ssh-keygen** 접속 · 샌드박스 VM)
| # | 폴더 | 배우는 것 | 실습 |
|---|---|---|---|
| 10 | [10_cloud_db](10_cloud_db/README.md) | **ssh-keygen**으로 VM 접속 → `tdfmini`로 **sqlite DB 생성**·연결 해부 | `tdfmini` on VM |
| 11 | [11_cron_daily](11_cron_daily/README.md) | **cron으로 매일 자동 수집** + "여러 날" 시뮬레이션·검증 | crontab |

| 기타 | | | |
|---|---|---|---|
| — | [exercises](exercises/README.md) | 연습문제(로컬+클라우드, +힌트) | — |
| — | [GLOSSARY.md](GLOSSARY.md) | 용어집(HTTP·XHR·XML·upsert·cron·SSH…) | — |

## 시작 전 (1분)

```powershell
# 프로젝트 루트에서
pip install requests          # 레슨 01~06에 필요 (이미 설치돼 있으면 생략)
pip install pytest            # 레슨 08에 필요
```

> 💡 학습용 스크립트는 **자기만의 연습용 DB**(`team_learning/playground.db`)에 저장합니다.
> 실제 운영 DB(`data/tdf.db`)는 건드리지 않으니 마음껏 실행/삭제해도 됩니다.

## 한글 출력 깨질 때 (윈도우)
윈도우 터미널은 기본 인코딩이 cp949라 한글 펀드명 출력 시 깨질 수 있습니다.
예제 스크립트 맨 위에 다음이 들어있습니다(이유는 레슨 04에서 설명):
```python
import sys; sys.stdout.reconfigure(encoding="utf-8")
```

## 🎤 슬라이드 (PPT)
| 데크 | 대상 | 내용 |
|---|---|---|
| **[instructor_slides.pptx](instructor_slides.pptx)** (22장) | 강사 | 진행 가이드 — 아젠다·타이밍·레슨별 핵심·라이브 데모 큐·함정 치트시트·체크포인트(발표자 노트 포함) |
| **[project_guide.pptx](project_guide.pptx)** (26장) | 학생 | 전체 프로젝트 따라하기 — ①소스 찾기 ②크롤러 ③DB 적재 ④자동화 ⑤클라우드 배포(코드·명령 그대로) |

- 재생성: `npm i pptxgenjs` 후 `node instructor_slides.build.js` / `node project_guide.build.js`

자, [00_setup](00_setup/README.md)부터 시작하세요. 천천히, 하나씩. 🚀
