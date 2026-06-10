"""레슨 03: KOFIA에 POST해서 '전체 펀드 기준가' 데이터를 한 번 받아온다.

실행:  python team_learning/03_first_crawl/crawl_v1.py

핵심 3가지만 기억하세요:
  1) 주소는 proframe'W'eb (대문자 W!)
  2) POST + XML 본문
  3) 본문은 .encode("utf-8") 해서 보낸다
"""
import sys
import requests

# 윈도우 터미널에서 한글이 깨지지 않도록(레슨 04에서 설명).
sys.stdout.reconfigure(encoding="utf-8")

URL = "https://dis.kofia.or.kr/proframeWeb/XMLSERVICES/"   # ← 대문자 W 주의!
DATE = "20260604"   # 최근 '평일'로 바꿔도 됩니다(휴장일/미래면 0건이 정상)

# 보낼 XML 본문: "기준가격(DISFundStdPriceSO)을, 이 날짜로, 전체 운용사(빈 값)로 조회"
BODY = f"""<?xml version="1.0" encoding="utf-8"?>
<message>
  <proframeHeader>
    <pfmAppName>FS-DIS2</pfmAppName>
    <pfmSvcName>DISFundStdPriceSO</pfmSvcName>
    <pfmFnName>select</pfmFnName>
  </proframeHeader>
  <systemHeader></systemHeader>
  <DISCondFuncDTO>
    <tmpV30>{DATE}</tmpV30>
    <tmpV11></tmpV11>
  </DISCondFuncDTO>
</message>"""

HEADERS = {
    "Content-Type": "application/xml; charset=UTF-8",
    "User-Agent": "Mozilla/5.0",   # "나 평범한 브라우저예요" 라고 알려주기
}


def main():
    print(f"요청: {URL}  날짜={DATE}")
    response = requests.post(URL, data=BODY.encode("utf-8"), headers=HEADERS, timeout=60)

    print("상태코드:", response.status_code)
    # <selectMeta> 한 덩어리 = 펀드 한 개. 몇 개나 받았는지 세어 보자.
    count = response.text.count("<selectMeta>")
    print("받은 펀드 수:", count, "개")

    if count == 0:
        print("\n0건이네요! 보통 원인:")
        print("  - 날짜가 휴장일/미래 → DATE를 최근 평일로 변경")
        print("  - 주소를 proframeweb(소문자)로 썼을 때 → proframeWeb(대문자 W) 확인")
    else:
        # 응답 맨 앞 selectMeta 한 덩어리만 살짝 구경
        start = response.text.find("<selectMeta>")
        print("\n첫 번째 펀드 데이터(앞부분):")
        print(response.text[start:start + 400])


if __name__ == "__main__":
    main()
