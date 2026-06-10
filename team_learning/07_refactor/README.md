# 07. 리팩터링 — 6주차 한 파일을 `tdfmini/`로 쪼개기

레슨 06의 [`tdf_onefile.py`](../06_one_file_crawler/tdf_onefile.py)(6주차 결과물)는 잘 동작합니다.
이제 **동작은 그대로, 구조만** 책임별로 나눕니다. **그 결과가 바로 이 학습 폴더 안의
[`tdfmini/`](../tdfmini/) 패키지**입니다. (레슨 08~11이 이 코드를 그대로 씁니다.)

## 왜 쪼개나 — 한 파일의 3가지 고통
1. **변경에 약함**: KOFIA가 컬럼 위치(`tmpV6`→`tmpV7`)를 바꾸면 코드 곳곳을 뒤져야 함.
2. **테스트 어려움**: 파싱만 떼어 시험하고 싶은데 네트워크·DB가 얽혀 있음.
3. **재사용 어려움**: "매일 실행"과 "과거 누적"이 같은 저장 로직을 복붙하게 됨.

## 어떻게 쪼갰나 — 6주차 파일의 주석 그대로
레슨 06 `tdf_onefile.py`엔 이미 `# (나중에 ~가 되는 부분)` 표시가 있었죠. 그대로 분리했습니다:

| 06 한 파일의 부분 | → tdfmini 파일 | 책임 |
|---|---|---|
| 맨 위 상수(URL·COL) | [`tdfmini/config.py`](../tdfmini/config.py) | **변하기 쉬운 것**만 한 곳에 |
| `fetch()` | [`tdfmini/fetch.py`](../tdfmini/fetch.py) | 받기(POST) |
| `parse_tdf()` | [`tdfmini/parse.py`](../tdfmini/parse.py) | **순수함수**: bytes→dict(네트워크·DB 없음) |
| `save()` | [`tdfmini/store.py`](../tdfmini/store.py) | 저장(스키마·멱등 upsert) |
| `main()` | [`tdfmini/run.py`](../tdfmini/run.py) | 흐름을 엮는 지휘자 + CLI |

## 직접 실행 (쪼갠 코드가 그대로 돈다)
```bash
cd team_learning
python -m tdfmini.run --company A01015 --date 20260610   # 교보악사, 최근 평일
#  → 수집 66건 → tdf_nav 총 66행   (DB: team_learning/playground.db)
python -m tdfmini.run --company A01015 --date 20260610   # 한 번 더 → 66행 그대로(멱등!)
```

## 무엇을 배웠나
- 좋은 구조는 처음부터가 아니라 **동작하는 코드를 정리하며** 나온다(= 리팩터링).
- "변하기 쉬운 것(config)" · "순수 로직(parse)" · "부작용(fetch/store)"을 **떼어 놓는다**.
- 이제 KOFIA가 바뀌면 보통 **`tdfmini/config.py`만** 고치면 된다(변경 국소화).

## 학습용 vs 실제 운영 코드
- 여기 `tdfmini/`는 **학습용 축소판**(dict 기반, 단순).
- 실제 운영 프로젝트 [`tdf_crawler/`](../../tdf_crawler/)는 **같은 아이디어의 큰 버전**
  (dataclass·이중 fetcher·테스트 50개 등). 둘은 *하는 일이 같고 규모만 다릅니다* — 비교해 보세요.

➡ 다음: [08_tdd](../08_tdd/README.md) — 쪼갰으니 `tdfmini.parse`를 테스트로 지킨다
