# 🧩 연습문제

직접 손으로 고쳐보며 익히는 게 가장 빠릅니다. 각 문제 아래 **힌트**가 접혀 있습니다.

> 모든 연습은 `team_learning/` 안의 학습용 스크립트와 `playground.db`로 합니다. 운영 DB는 건드리지 않아요.

---

### 연습 1 — 날짜 바꿔보기 (난이도 ★)
`03_first_crawl/crawl_v1.py`의 `DATE`를 **오늘이 아닌 최근 평일**로 바꿔 실행하고, 받은 펀드 수를 비교해 보세요.
주말/공휴일로 바꾸면 몇 건이 나오나요?

<details><summary>힌트</summary>

주말·공휴일은 공시가 없어 **0건**이 정상입니다. 평일이라도 너무 최근(당일 오전)이면 아직 공시 전일 수 있어요.
</details>

---

### 연습 2 — 순자산도 함께 뽑기 (난이도 ★★)
`04_parse_xml/parse_v2.py`가 기준가만 출력합니다. **순자산(`tmpV9`)** 도 같이 출력하도록 바꿔보세요.

<details><summary>힌트</summary>

`docs/schema`에서 순자산이 `tmpV9`(백만원)임을 확인 → 출력 줄에 `float(f.get("tmpV9") or 0)` 추가.
</details>

---

### 연습 3 — 멱등성 직접 증명 (난이도 ★★)
`06_one_file_crawler/tdf_onefile.py`를 **세 번** 실행하고, 매번 총 행 수가 같은지 확인하세요.
그다음 `PRIMARY KEY (...)` 줄과 `ON CONFLICT ...` 줄을 지우고 다시 두 번 실행하면 어떻게 되나요?

<details><summary>힌트</summary>

PK/ON CONFLICT를 지우면 매 실행마다 행이 **두 배·세 배**로 늘어납니다 = 멱등성이 깨진 것.
(확인 후 원복하세요. 또는 `playground.db` 파일을 지우고 다시 시작.)
</details>

---

### 연습 4 — 운용사로 거르기 (난이도 ★★)
`06`의 `parse_tdf()`를 고쳐, TDF 중에서 **특정 운용사(예: '미래에셋')** 만 저장하도록 조건을 추가하세요.

<details><summary>힌트</summary>

`if "TDF" not in name.upper(): continue` 아래에
`if "미래에셋" not in r.get(COL["manager"], ""): continue` 한 줄 추가.
</details>

---

### 연습 5 — 보수(TER) 크롤러 만들기 (난이도 ★★★)
`06`을 본떠, **보수** 데이터를 받는 미니 스크립트를 만들어 보세요.
- 서비스이름: `DISFundFeeCmsSO`, 날짜: 최근 **월말**(예: `20260430`)
- 뽑을 값: 펀드코드 `tmpV15`, 합성총보수 `tmpV12`(%)

<details><summary>힌트</summary>

`06`의 `fetch()`에서 `pfmSvcName`만 `DISFundFeeCmsSO`로 바꾸고 `DATE`를 월말로.
파싱은 같은 `selectMeta` 구조. 컬럼만 `tmpV15`(코드)·`tmpV12`(TER)로. 실제 정답 구조는
[tdf_crawler/parsers.py](../../tdf_crawler/parsers.py)의 `map_fees` 참고.
</details>

---

### 연습 6 — 테스트 추가 (난이도 ★★★)
`08_tdd/test_example.py`의 `parse_number`에 대해, **음수**(`"-300"`)와 **공백 포함**(`" 12 "`) 케이스의
테스트를 추가하고 통과시키세요.

<details><summary>힌트</summary>

`assert parse_number("-300") == -300.0` / `assert parse_number(" 12 ") == 12.0`
(현재 함수가 이미 통과시키는지 확인 — 통과하면 함수가 견고하다는 뜻!)
</details>

---

## ☁️ Part 2 — 클라우드/cron 연습 (레슨 10·11)
> VM에 접속해 `~/tdf-crawler`에서 진행. 운영 DB가 아닌 연습이므로 마음껏 돌려도 됩니다.

### 연습 7 — 클라우드에 DB 생성 확인 (난이도 ★★)
VM에서 하루치를 수집하고, `data/tdf.db`가 생겼는지 + 어떤 표에 몇 행 들어갔는지 확인하세요.

<details><summary>힌트</summary>

`.venv/bin/python -m tdf_crawler.run --date 2026-06-10` → `ls -lh data/tdf.db` →
레슨 10의 파이썬 조회 스니펫으로 `nav_daily` 행수·날짜 확인.
</details>

### 연습 8 — "여러 날" 시뮬레이션으로 시계열 만들기 (난이도 ★★)
`--date`를 바꿔 3일치를 연속 수집해 `nav_daily`에 날짜가 3개 쌓이는 걸 보이세요. 그다음 **같은 날을 또**
실행해도 행수가 안 늘어남(멱등)을 증명하세요.

<details><summary>힌트</summary>

`for d in 2026-06-08 2026-06-09 2026-06-10; do .venv/bin/python -m tdf_crawler.run --date $d; done`
→ 날짜 3개. 같은 날 재실행 후 `SELECT COUNT(*)` 동일 → 멱등 OK.
</details>

### 연습 9 — cron 등록하고 "내일" 확인 (난이도 ★★★)
매일 08:00 실행되도록 `crontab`을 등록하고, `crontab -l`로 확인하세요. 내일 `verify.sh`로 날짜가
하나 더 늘었는지 확인하는 것까지가 숙제입니다.

<details><summary>힌트</summary>

레슨 11의 `echo "0 8 * * * ..." | crontab -` 직접 등록. `( crontab -l | grep ...)` 방식의 함정 주의.
`systemctl is-active cron`이 `active`인지도 확인.
</details>

---

## 다 풀었다면
실제 코드와 비교해 보세요. 당신이 손으로 만든 미니 버전과 `tdf_crawler/`의 정식 버전은
**같은 일을 하되 구조가 다릅니다**. 그 차이를 설명할 수 있다면 — 이 프로젝트를 이해한 겁니다. 🎓
