"""tdfmini — 레슨 06의 한 파일 크롤러를 책임별로 쪼갠 '학습용' 미니 크롤러.

레슨 07(리팩터링)의 결과물입니다. 실제 운영 패키지(`tdf_crawler`)의 축소판이지만,
초보자가 읽기 쉽게 dict 기반·단순 구조로 만들었습니다.
  config.py  변하기 쉬운 것(URL·컬럼맵)
  fetch.py   받기(POST)
  parse.py   파싱(selectMeta/tmpV) — 순수함수
  store.py   저장(sqlite, 멱등 upsert)
  run.py     지휘자(받기→파싱→저장) + CLI
  backfill.py 과거 누적(레슨 09)
"""
