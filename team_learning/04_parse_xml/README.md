# 04. 파싱 — 받은 XML에서 원하는 값만 뽑기

레슨 03에서 받은 응답은 거대한 XML 덩어리입니다. 여기서 **펀드코드·이름·기준가**만 뽑아봅니다.

## 응답 한 펀드(selectMeta)의 모습
```xml
<selectMeta>
  <tmpV1>교보악사자산운용</tmpV1>      <!-- 운용사 -->
  <tmpV2>교보악사평생든든적격TDF2045…</tmpV2>  <!-- 펀드명 -->
  <tmpV6>1927.46</tmpV6>            <!-- 기준가(원) -->
  <tmpV12>K55207CP6080</tmpV12>     <!-- 펀드코드 -->
  <tmpV14>20260604</tmpV14>         <!-- 기준일 -->
  ...
</selectMeta>
```
> 어떤 `tmpV`가 무슨 뜻인지는 [docs/schema](../../docs/schema/README.md) 표에 정리돼 있습니다.
> 이 "위치→의미" 약속이 흐트러지면 안 되니, 실제 프로젝트는 이걸 `config.py` 한 곳에 모아둡니다(레슨 07).

## 파싱 도구: `xml.etree.ElementTree` (파이썬 내장)
```python
from xml.etree import ElementTree as ET
root = ET.fromstring(xml_bytes)
for el in root.iter():           # 모든 태그를 훑으며
    if el.tag.endswith("selectMeta"):   # 펀드 한 덩어리를 만나면
        ...                      # 그 안의 tmpV들을 읽는다
```

## 직접 실행
```powershell
python team_learning/04_parse_xml/parse_v2.py
```
→ TDF(펀드명에 'TDF' 포함) 펀드 5개의 **코드 · 기준가 · 이름**이 깔끔히 출력됩니다.

## 무엇을 배웠나
- XML은 `ElementTree`로 파싱한다(설치 불필요, 내장).
- "펀드명에 TDF 포함" 같은 간단한 조건으로 **원하는 펀드만 거른다**(이게 곧 'TDF 탐색').
- 숫자 문자열(`"1927.46"`)은 `float()`로 숫자로 바꾼다.
- `sys.stdout.reconfigure(encoding="utf-8")`: 윈도우에서 한글 출력이 깨지는 걸 막는 한 줄.

## 실제 프로젝트 연결
이 파싱이 `tdf_crawler/parsers.py`입니다. 거기선 값을 dict가 아니라 **dataclass**(NavRecord 등)로 담아
타입을 분명히 하고, "TDF 거르기"는 `tdf_crawler/discovery.py`로 분리돼 있습니다.

➡ 다음: [05_save_sqlite](../05_save_sqlite/README.md) — 뽑은 값을 저장하기
