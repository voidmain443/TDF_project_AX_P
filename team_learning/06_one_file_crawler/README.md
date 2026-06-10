# 06. 동작하는 한 파일 크롤러 (MVP) + 멱등성

지금까지 배운 받기·파싱·저장을 **한 파일**로 합치고, 레슨 05의 "중복" 문제를 해결합니다.
이게 바로 **MVP(최소 동작 제품)** — 실제 프로젝트의 출발점입니다.

## 새로 배우는 핵심: PRIMARY KEY + upsert = 멱등성
- 표에 `PRIMARY KEY (fund_code, base_date)` 를 주면 = "한 펀드는 한 날짜에 딱 한 행".
- 저장은 `INSERT ... ON CONFLICT(...) DO UPDATE` (= **upsert**): 같은 키가 이미 있으면 **덮어쓰기**.
- 그래서 **몇 번을 실행해도 행 수가 안 늘어납니다** → 이것이 **멱등성**. 매일 자동 실행의 필수 조건!

## 직접 실행 (두 번 실행해 보세요!)
```powershell
python team_learning/06_one_file_crawler/tdf_onefile.py
python team_learning/06_one_file_crawler/tdf_onefile.py   # 한 번 더!
```
두 번째 실행에도 **행 수가 그대로**면 성공. (레슨 05는 두 배가 됐었죠)

## 무엇을 배웠나
- 받기→파싱→저장을 함수로 나눠 하나의 흐름으로 묶는다.
- `PRIMARY KEY` + `ON CONFLICT DO UPDATE`로 **중복 없이 갱신**(멱등).
- 이제 이 스크립트를 매일 돌리면 "그날 스냅샷"이 안전하게 쌓인다.

## "그런데 코드가 길어지네…" (다음 레슨의 동기)
한 파일에 URL·컬럼위치·파싱·저장·실행이 다 섞여 있습니다. 지금은 괜찮지만:
- KOFIA가 컬럼 위치를 바꾸면? → 어디를 고쳐야 할지 찾기 어려움.
- 테스트하려면? → 네트워크 없이 파싱만 떼어 시험하기 어려움.
➡ 그래서 **레슨 07**에서 config/parser/db로 **분리(리팩터링)** 합니다.

## 실제 프로젝트 연결
이 한 파일이 자라서 `tdf_crawler/` 패키지가 됩니다.
`run.py`(흐름) = 이 파일의 `main()`, `db.py` = 저장부, `parsers.py` = 파싱부, `config.py` = 맨 위 상수들.

➡ 다음: [07_refactor](../07_refactor/README.md)
