"""레슨 01: requests로 웹페이지를 가져오는 가장 단순한 예제.

실행:  python team_learning/01_http_basics/example.py
"""
import sys
import requests

# 윈도우 터미널에서 한글 출력이 깨지지 않도록(레슨 04에서 자세히 설명).
sys.stdout.reconfigure(encoding="utf-8")


def main():
    url = "https://dis.kofia.or.kr/"   # KOFIA 전자공시 홈페이지

    # GET 요청 한 줄. "이 주소의 페이지 주세요" 라는 뜻.
    response = requests.get(url, timeout=20)

    print("요청한 주소 :", url)
    print("상태코드    :", response.status_code, "(200이면 성공!)")
    print("응답 길이   :", len(response.text), "글자")
    print("응답 앞부분 :")
    print(response.text[:200])   # 본문 앞 200글자만 살짝 구경


if __name__ == "__main__":
    main()
