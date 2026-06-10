# 09. 멱등성 · 과거 누적 (tdfmini)

이제 "한 번 받는 코드"를 **안전하게, 과거까지** 쌓습니다.

## 1) 멱등성 (이미 레슨 06~07에서 체험)
- `PRIMARY KEY (fund_code, base_date)` + `upsert`([`tdfmini/store.py`](../tdfmini/store.py)) → **몇 번 돌려도 중복 없음**.
- 왜 중요? 자동화는 실패·재시도가 잦습니다. 멱등하면 **그냥 다시 돌리면** 복구됩니다.
```bash
cd team_learning
python -m tdfmini.run --company A01015 --date 20260610   # 66행
python -m tdfmini.run --company A01015 --date 20260610   # 66행 그대로 = 멱등 OK
```

## 2) 어떻게 쌓이나 — "그날 스냅샷 1장씩"
- 한 번 실행 = 그날 날짜(`base_date`)의 TDF 한 장을 **추가**. 과거는 그대로 보존.
- 표가 `2026-06-08`, `06-09`, `06-10` … 날짜별로 늘어남 → **시계열**.

## 3) 과거 데이터 한 번에 채우기 (백필)
[`tdfmini/backfill.py`](../tdfmini/backfill.py)가 영업일을 돌며 며칠치를 쌓습니다:
```bash
cd team_learning
python -m tdfmini.backfill 2026-06-04 2026-06-10 2026-06-04   # 시작 끝 (운용사 기본 교보악사)
#  2026-06-04: 66건 / 06-05: 66건 / 06-08: 66건 ...
```
- 평일(월~금)만, 휴장일은 0건으로 자동 스킵.
- 멱등이라 다시 돌려도 중복 안 쌓임.

## 무엇을 배웠나
- **멱등성** 덕분에 자동화·재시도·복구가 안전하다.
- 매일 실행은 "그날 스냅샷"을 시계열로 **누적**한다(덮어쓰기 아님).
- 과거는 `backfill`로 채우고, 이후는 스케줄러(cron)가 매일 한 장씩 더한다(레슨 11).

## ✅ Part 1(로컬) 완료 — 이제 클라우드로
```
받기 → 파싱 → 저장 → 한 파일 MVP → tdfmini로 분리 → 테스트 → 멱등·백필
```
진짜 가치는 **클라우드에서 매일 무인으로 도는 것**입니다.

➡ **Part 2로**: [10_cloud_db](../10_cloud_db/README.md) — 샌드박스 VM에 ssh-keygen으로 접속해 tdfmini로 클라우드 DB 만들기
→ [11_cron_daily](../11_cron_daily/README.md) — cron으로 매일 자동 수집

- 운영(실제 `tdf_crawler`) 배포 표준은 [docs/DEPLOY.md](../../docs/DEPLOY.md) · 손으로 더: [exercises](../exercises/README.md)
