# 📊 분석가(Analyst) 문서

> 대상: 적재된 `tdf.db`로 분석을 수행하고, 분석팀을 구성·운영하는 사람.

## 1. 시작하기 (안전한 접근)

- DB는 **읽기 전용으로** 다루세요. 운영 DB에 직접 쿼리하지 말고 **복제본/백업본**을 받아 분석:
  ```bash
  cp data/tdf.db analysis_copy.db        # 또는 운영자의 .backup 산출물 사용
  sqlite3 analysis_copy.db
  ```
- 운영 파일을 꼭 열어야 하면 읽기전용 URI로:
  ```python
  import sqlite3
  con = sqlite3.connect("file:data/tdf.db?mode=ro", uri=True)
  ```

## 2. 스키마 & 조인

> 전체 **ER 다이어그램 + 컬럼별 데이터 사전**은 [docs/schema](../schema/README.md) 참고.

키는 모두 **`(fund_code, base_date)`** (펀드 클래스 × 날짜). `funds`만 날짜 무관 메타.

```
funds(fund_code PK, fund_name, manager, fund_type, vintage_year, first_seen, last_seen)
nav_daily(fund_code, base_date, nav, aum_settlement, net_assets)         -- 일별
flows_daily(fund_code, base_date, inflow, outflow, net_flow)            -- 일별(파생)
fees(fund_code, base_date, ter_synthetic, mgmt_fee, sales_fee)          -- 월별(월말)
crawl_runs(...)                                                          -- 수집 메타(분석 제외)
```
표준 조인:
```sql
SELECT f.fund_name, f.manager, f.vintage_year, n.*
FROM nav_daily n JOIN funds f USING(fund_code)
WHERE n.base_date = '2026-06-04';
```

## 3. ⚠️ 단위·품질 주의 (분석 전 필독)

| 항목 | 주의 |
|---|---|
| `nav` | **원** 단위 기준가 |
| `aum_settlement`(설정액), `net_assets`(순자산) | **백만원**. 원 환산 ×1,000,000 |
| `ter_synthetic`,`mgmt_fee`,`sales_fee` | **% (연)**. 0.7 = 0.7% |
| `net_assets = 0` | 재간접/母 클래스 다수가 0으로 공시 → **규모 지표는 `aum_settlement` 사용** |
| 클래스 중복 | 한 펀드가 ClassA/C/P… 여러 코드. 펀드 본질 집계는 이름/母코드 기준 별도 처리 |
| `fees` 시차 | 월별·1~2개월 지연. 최신 `base_date`만 "현재 보수"로 사용 |
| `flows` 첫날/연휴 | 직전 영업일 대비 Δ. 펀드 최초 적재일은 NULL, 연휴는 직전 영업일 대비로 이어짐 |
| 보수 NULL | 母/기관 클래스는 소매 보수 없음(정상) |

## 4. 분석 쿼리 레시피

### 4.1 일별 수익률 (기준가 변화율)
```sql
SELECT fund_code, base_date,
       nav / LAG(nav) OVER (PARTITION BY fund_code ORDER BY base_date) - 1 AS daily_return
FROM nav_daily
WHERE fund_code = 'K55207CP6080'
ORDER BY base_date;
```

### 4.2 기간 누적수익률 Top 10 (빈티지 필터)
```sql
WITH r AS (
  SELECT n.fund_code,
         FIRST_VALUE(nav) OVER (PARTITION BY n.fund_code ORDER BY base_date) AS first_nav,
         LAST_VALUE(nav)  OVER (PARTITION BY n.fund_code ORDER BY base_date
                                ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_nav
  FROM nav_daily n
)
SELECT f.fund_name, f.vintage_year, MAX(last_nav/first_nav - 1) AS period_return
FROM r JOIN funds f USING(fund_code)
WHERE f.vintage_year = 2045
GROUP BY f.fund_code ORDER BY period_return DESC LIMIT 10;
```

### 4.3 설정액(AUM) 추이 & 순유입 랭킹
```sql
-- 최근일 기준 순유입 상위(자금 유입 강한 펀드)
SELECT f.fund_name, f.manager, fl.net_flow
FROM flows_daily fl JOIN funds f USING(fund_code)
WHERE fl.base_date = (SELECT MAX(base_date) FROM flows_daily)
ORDER BY fl.net_flow DESC LIMIT 20;
```

### 4.4 빈티지(목표연도)별 집계 — 글라이드패스 관점
```sql
SELECT f.vintage_year,
       COUNT(DISTINCT f.fund_code)        AS classes,
       SUM(n.aum_settlement)              AS aum_백만원,
       AVG(fe.ter_synthetic)             AS avg_ter_pct
FROM funds f
JOIN nav_daily n ON n.fund_code=f.fund_code AND n.base_date=(SELECT MAX(base_date) FROM nav_daily)
LEFT JOIN fees fe ON fe.fund_code=f.fund_code AND fe.base_date=(SELECT MAX(base_date) FROM fees)
WHERE f.vintage_year IS NOT NULL
GROUP BY f.vintage_year ORDER BY f.vintage_year;
```

### 4.5 운용사별·보수 비교
```sql
SELECT f.manager, AVG(fe.ter_synthetic) avg_ter, MIN(fe.ter_synthetic) min_ter, MAX(fe.ter_synthetic) max_ter
FROM fees fe JOIN funds f USING(fund_code)
WHERE fe.base_date=(SELECT MAX(base_date) FROM fees)
GROUP BY f.manager ORDER BY avg_ter;
```

## 5. 데이터 품질 체크 (분석 전 위생)
```sql
-- 적재된 날짜 수와 범위
SELECT COUNT(DISTINCT base_date), MIN(base_date), MAX(base_date) FROM nav_daily;
-- 순자산 0 비율(규모지표 선택 근거)
SELECT AVG(net_assets=0)*100 AS pct_zero_netassets FROM nav_daily
WHERE base_date=(SELECT MAX(base_date) FROM nav_daily);
-- 기준가 결측/이상
SELECT COUNT(*) FROM nav_daily WHERE nav IS NULL OR nav<=0;
-- 보수 매칭률(보수 있는 TDF 비율)
SELECT (SELECT COUNT(DISTINCT fund_code) FROM fees)*1.0/(SELECT COUNT(*) FROM funds) AS fee_coverage;
```

## 6. pandas 연동
```python
import sqlite3, pandas as pd
con = sqlite3.connect("file:analysis_copy.db?mode=ro", uri=True)
nav = pd.read_sql("SELECT * FROM nav_daily", con, parse_dates=["base_date"])
funds = pd.read_sql("SELECT * FROM funds", con)
# 일별 수익률 매트릭스
wide = nav.pivot_table(index="base_date", columns="fund_code", values="nav").sort_index()
returns = wide.pct_change()
# 빈티지 부착
nav = nav.merge(funds[["fund_code","vintage_year","manager"]], on="fund_code")
```

## 7. 분석팀 구성 제안

| 역할 | 책임 | 본 DB에서 다루는 부분 |
|---|---|---|
| **데이터 엔지니어** | 적재 신뢰성, 분석 마트/뷰, 복제본 파이프라인 | `crawl_runs` 모니터, 정합성 뷰(클래스 합산/단위환산), 운영자와 접점 |
| **퀀트/리서치** | 수익률·위험·글라이드패스 분석, 빈티지 비교 | `nav_daily`(수익률), `funds.vintage_year`, 벤치마크(향후 returns 피드) |
| **리스크/규정** | 보수·비용 적정성, 자금흐름 이상 탐지 | `fees`(TER), `flows_daily`(유출입 급변) |
| **BI/시각화** | 대시보드(AUM·순유입·TER 트렌드) | 위 4절 레시피를 BI 도구에 연결 |

### 협업 인터페이스
- **데이터 요구 → 설계자**: 필요한 새 지표(수익률·벤치마크·실측 유출입 등)는 설계자에게 피드 추가 요청
  (설계자 문서 4절 로드맵과 연계). 단위·정의를 문서로 합의.
- **품질 이슈 → 개발자/운영자**: 결측·이상치·구조변경 의심은 `crawl_runs`·행수와 함께 리포트.
- **재현성**: 분석은 항상 백업 스냅샷(날짜 명시) 기준으로 수행 → 결과 재현 가능. 운영 DB 직접 수정 금지.

## 8. 자주 묻는 한계
- **현재 없는 것**: 공식 수익률·벤치마크·자산배분(글라이드패스)·실측 설정/해지액. (설계자 로드맵 참고)
- **보수는 월 스냅샷**: 일 단위 보수 변화는 분석 불가(원천이 월 공시).
- **클래스 vs 펀드**: 기본 단위는 클래스. 母펀드 단위 분석은 별도 집계 규칙 필요(데이터 엔지니어 담당 권장).
