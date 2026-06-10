# 03. 첫 크롤링 — KOFIA에 POST해서 진짜 데이터 받기

레슨 02에서 관찰한 그 "몰래 요청"을 코드로 흉내 냅니다. 드디어 진짜 데이터를 받습니다!

## 보낼 XML 본문 뜯어보기
```xml
<message>
  <proframeHeader>
    <pfmAppName>FS-DIS2</pfmAppName>
    <pfmSvcName>DISFundStdPriceSO</pfmSvcName>   <!-- "기준가격 데이터 주세요" -->
    <pfmFnName>select</pfmFnName>
  </proframeHeader>
  <systemHeader></systemHeader>
  <DISCondFuncDTO>
    <tmpV30>20260604</tmpV30>   <!-- 날짜(YYYYMMDD) -->
    <tmpV11></tmpV11>           <!-- 운용사코드: 비우면 '전체 운용사' -->
  </DISCondFuncDTO>
</message>
```

## 직접 실행
```powershell
python team_learning/03_first_crawl/crawl_v1.py
```
실행하면 **"selectMeta 26000여 개"** 처럼 펀드 개수가 출력됩니다. 전체 펀드 데이터를 한 번에 받은 것!

## 무엇을 배웠나
- `requests.post(url, data=본문, headers=...)` 로 조회 요청을 보낸다.
- 본문은 **bytes로 인코딩**해서 보낸다(`body.encode("utf-8")`) — 한글 안 깨지게.
- 헤더 `Content-Type: application/xml` 로 "나 XML 보낸다"고 알려준다.
- 응답에 `<selectMeta>` 가 몇 개인지 세면 받은 펀드 수를 알 수 있다.

## 흔한 실수
- 주소를 `proframeweb`(소문자)로 쓰면 0건/에러 → `proframeWeb`(대문자 W).
- 날짜를 **휴장일/미래**로 주면 0건이 정상. 최근 **평일** 날짜로 바꿔보세요.

## 실제 프로젝트 연결
이 한 번의 요청이 바로 `tdf_crawler/fetchers/http_fetcher.py`의 `fetch()` 입니다.
보낼 XML을 만드는 부분은 `tdf_crawler/fetchers/base.py`의 `build_envelope()`.

➡ 다음: [04_parse_xml](../04_parse_xml/README.md) — 받은 XML에서 값 뽑기
