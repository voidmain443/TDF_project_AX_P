# 05. 저장 — 뽑은 값을 SQLite에 넣기

받은 데이터를 출력만 하면 사라집니다. **저장**해야 나중에 분석할 수 있죠. 파이썬 내장 `sqlite3`를 씁니다.

## SQLite가 좋은 이유
- 설치 불필요(파이썬 내장), **파일 하나(`*.db`)가 곧 DB**.
- 백업=파일 복사, 조회=SQL. 가볍고 이식 쉬움.

## 핵심 4단계
```python
import sqlite3
con = sqlite3.connect("playground.db")          # 1) 연결(파일 생성)
con.execute("CREATE TABLE IF NOT EXISTS nav (...)")  # 2) 표 만들기
con.execute("INSERT INTO nav VALUES (?, ?, ?)", (...))  # 3) 행 넣기 (?는 안전한 값 끼우기)
con.commit()                                    # 4) 저장 확정
```

## 직접 실행
```powershell
python team_learning/05_save_sqlite/save_v3.py
```
→ `team_learning/playground.db` 파일이 생기고, TDF 기준가가 저장됩니다. 마지막에 저장된 개수를 출력.

## 저장 후 직접 확인
```powershell
python -c "import sqlite3; print(sqlite3.connect('team_learning/playground.db').execute('SELECT * FROM nav LIMIT 5').fetchall())"
```

## 무엇을 배웠나
- `sqlite3.connect("파일.db")` → 표 생성 → `INSERT` → `commit()`.
- 값은 문자열로 직접 붙이지 말고 **`?` 자리표시자**로 넣는다(안전·정확).
- 표를 만들 땐 어떤 열(컬럼)에 무엇을 넣을지 미리 정한다.

## 아직 부족한 점 (다음 레슨 예고)
- 같은 날 또 실행하면? → **중복**이 쌓입니다 😱. 이걸 막는 게 레슨 06의 **upsert/멱등성**.

## 실제 프로젝트 연결
저장은 `tdf_crawler/db.py`. 거기선 중복을 막는 `PRIMARY KEY (fund_code, base_date)` +
`INSERT ... ON CONFLICT DO UPDATE`(upsert)를 씁니다(레슨 06에서 직접 해봅니다).

➡ 다음: [06_one_file_crawler](../06_one_file_crawler/README.md) — 전부 합쳐 '동작하는 크롤러' 완성
