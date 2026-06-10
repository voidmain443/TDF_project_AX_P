# 02. 사이트는 데이터를 어떻게 주는가? (관찰하기)

> 코드를 짜기 전에 **"무엇을 흉내 낼지"** 부터 알아야 합니다. 이 레슨은 실행 코드 없이 "관찰"이 핵심.

## 두 종류의 웹사이트

1. **HTML에 데이터가 박혀 있는 사이트** → `requests.get` 후 HTML만 파싱하면 끝(쉬움).
2. **화면은 비어 있고, 자바스크립트가 뒤에서 데이터를 따로 받아오는 사이트** ← KOFIA가 이 유형.
   - 주소창은 그대로인데 표 데이터만 슥 채워지죠? 그건 **XHR**(뒤에서 몰래 주고받는 요청) 때문입니다.
   - 그래서 우리는 그 "몰래 요청"을 **그대로 흉내** 내야 합니다.

## 직접 관찰해 보기 (브라우저) — 천천히, 클릭 단위로

### 먼저 큰 그림 (이게 핵심!)
KOFIA의 **모든** 데이터 요청은 **같은 주소** `…/proframeWeb/XMLSERVICES/` 로 갑니다.
페이지를 열면 메뉴·날짜목록·운용사목록 등 여러 요청이 *동시에 같은 주소로* 나가요.
그래서 "**검색 버튼이 보내는 그 하나**"를 골라내는 게 관건입니다. (구분법은 5번)

### 단계 (정확히 이대로)
1. 크롬에서 페이지 열기:
   `https://dis.kofia.or.kr/websquare/index.jsp?w2xPath=/wq/fundann/DISFundStdPrice.xml`
   → 화면에 **운용사 선택 · 기준일자** 같은 조회조건 폼이 보입니다.
2. `F12` → **Network** 탭. 상단에서 3가지 준비:
   - **Fetch/XHR** 필터 클릭 (이미지·CSS 잡음 숨김)
   - **Preserve log** 체크 (화면 갱신돼도 기록 유지)
   - 왼쪽 🚫(Clear)로 목록 한 번 비우기
3. 화면에서 **운용사를 하나 선택**(예: 삼성자산운용) + **기준일자**를 최근 **평일**로.
   ⚠️ 운용사를 안 고르면 결과가 비거나 에러가 납니다.
4. **검색** 버튼 클릭.
5. 목록에 `XMLSERVICES` 가 여러 개 뜹니다(다 같은 주소!). **데이터 요청 고르는 법**:
   - **Size(크기) 열로 정렬** → 방금 뜬 **가장 큰(수 MB)** 항목이 데이터예요.
   - 클릭 → **Payload(요청)** 탭에 `<pfmSvcName>DISFundStdPriceSO</pfmSvcName>` 가 있으면 **정답**.
6. 그 항목의 탭 읽기:
   - **Headers**: Request URL = `…/proframeWeb/XMLSERVICES/` (대문자 **W**!), Method **POST**
   - **Payload**: XML 본문 — `pfmSvcName` · `tmpV30`(날짜) · `tmpV11`(운용사코드)
   - **Response / Preview**: `<selectMeta>` 가 잔뜩, 그 안 `<tmpV6>`=기준가 등

### 😵 "안 떠요 / 못 찾겠어요" — 막혔을 때 (대부분 여기서 막힘)
| 증상 | 원인 | 해결 |
|---|---|---|
| XMLSERVICES가 너무 많아 헷갈림 | 모든 서비스가 같은 주소 사용 | **Size로 정렬**해 가장 큰 것 → Payload의 `pfmSvcName=DISFundStdPriceSO` 확인 |
| 검색해도 새 요청이 안 뜸 | 필터/로그 미설정 | **Fetch/XHR** 필터·**Preserve log** 켜기, 운용사 선택했는지 |
| 결과가 0건/비어있음 | 휴장일·미래 날짜·운용사 미선택 | 기준일자를 **최근 평일**로, 운용사 선택 |
| 응답이 너무 크고 느려서 멈춤 | 운용사를 '전체'로 받음(약 36MB) | **운용사 하나만** 고르면 ~3.7MB로 빨라짐 |
| 페이지가 안 열림/느림 | 일시적 | 새로고침, 잠시 대기 |

### 🅰 가장 빠른 우회 — "Copy as cURL"
요청을 못 고르겠으면: 아무 **XMLSERVICES POST 우클릭 → Copy → Copy as cURL**.
거기에 **URL·헤더·본문(XML)** 이 통째로 들어 있어, 붙여넣어 보면 정답이 한눈에 보입니다.

### 🅱 관찰이 안 되면 그냥 진행하세요 (수업이 멈추지 않게)
이 레슨의 목적은 "**어떤 요청인지 이해**"지, 화면 캡처 자체가 아닙니다.
아래가 우리가 이미 확인한 **정답**이고, **지금도 작동**합니다(라이브 검증됨). 바로 레슨 03으로 가도 됩니다.

| 항목 | 값 |
|---|---|
| 요청 URL | `https://dis.kofia.or.kr/proframeWeb/XMLSERVICES/` (대문자 W) |
| 메서드/헤더 | `POST` · `Content-Type: application/xml; charset=UTF-8` |
| 본문 핵심 | `pfmSvcName=DISFundStdPriceSO` · `tmpV30=날짜(YYYYMMDD)` · `tmpV11=운용사(빈값=전체)` |
| 응답 | `<selectMeta>` = 펀드 1개 · `tmpV12`=코드 `tmpV2`=이름 `tmpV6`=기준가 `tmpV5`=설정액 `tmpV14`=날짜 |

### ✅ DevTools 없이 1초로 "이게 맞다" 증명 (운용사 코드로 작게·빠르게)
```python
import requests
URL = "https://dis.kofia.or.kr/proframeWeb/XMLSERVICES/"        # 대문자 W!
body = """<?xml version="1.0" encoding="utf-8"?>
<message><proframeHeader><pfmAppName>FS-DIS2</pfmAppName>
<pfmSvcName>DISFundStdPriceSO</pfmSvcName><pfmFnName>select</pfmFnName></proframeHeader>
<systemHeader></systemHeader>
<DISCondFuncDTO><tmpV30>20260610</tmpV30><tmpV11>A01005</tmpV11></DISCondFuncDTO></message>"""
# tmpV30=최근 평일로, tmpV11=A01005(삼성)·A01048(미래에셋) 같은 운용사 코드(작고 빠름)
r = requests.post(URL, data=body.encode("utf-8"),
                  headers={"Content-Type":"application/xml; charset=UTF-8","User-Agent":"Mozilla/5.0"}, timeout=30)
print(r.status_code, r.text.count("<selectMeta>"), "개 펀드")   # 200 과 펀드 수가 나오면 성공!
```
> 💡 운용사 비우면(`<tmpV11></tmpV11>`) 전체 2.6만 펀드·36MB라 느립니다. **수업 땐 운용사 코드로 좁히세요**(약 3.7MB, 2~3초).

> 실제로 이 프로젝트도 **브라우저로 이 요청을 캡처**해 주소·서비스이름·컬럼 위치를 알아냈습니다.
> (그 과정은 루트 [DATA.md](../../DATA.md) 1절 참고)

## 핵심 깨달음 3가지
1. KOFIA 데이터는 GET이 아니라 **POST + XML 본문**으로 받아온다.
2. 보낼 것: `pfmSvcName`(어떤 데이터인지) + `tmpV30`(날짜) + `tmpV11`(운용사, 비우면 전체).
3. 받을 것: `<selectMeta>` 한 덩어리가 펀드 한 개, 그 안 `tmpV6`=기준가, `tmpV12`=펀드코드 …
   (위치 의미는 [docs/schema](../../docs/schema/README.md)에 표로 정리돼 있음)

## ⚠️ 왜 주소에 대문자 W?
`proframe**W**eb` 입니다. 소문자 `proframeweb`는 **죽은 옛 주소**라 요청하면 엉뚱한 에러페이지로
튕겨서 "0건"이 나옵니다. (실제로 이 프로젝트 초반에 이 한 글자 때문에 한참 헤맸습니다 😅)

➡ 다음: [03_first_crawl](../03_first_crawl/README.md) — 이제 코드로 흉내 내봅니다.
