# 01. HTTP 기초 — 코드로 웹페이지 가져오기

## 개념 (비유로)
브라우저에서 주소를 치면 → 브라우저가 서버에 **"이 페이지 주세요(요청)"** → 서버가 **"여기 있어요(응답)"**.
크롤링은 이 대화를 **브라우저 대신 코드로** 하는 것입니다. 도구는 `requests` 라이브러리.

- **요청(request)**: 우리가 보냄. 주소(URL) + 방식(GET/POST) + (POST면) 본문.
- **응답(response)**: 서버가 줌. **상태코드**(200=성공) + **본문**(HTML/XML/JSON 등).

## 직접 실행
```powershell
python team_learning/01_http_basics/example.py
```

## 코드 (example.py 미리보기)
```python
import requests
r = requests.get("https://dis.kofia.or.kr/")   # GET 요청
print("상태코드:", r.status_code)               # 200이면 성공
print("응답 길이:", len(r.text), "글자")
```

## 무엇을 배웠나
- `requests.get(url)` 한 줄로 웹페이지를 가져온다.
- 응답에는 **상태코드**(`r.status_code`)와 **본문**(`r.text`)이 있다.
- `200`은 성공. 만약 `307`(다른 곳으로 보냄)·`404`(없음)·`500`(서버오류)이면 뭔가 잘못된 것.

> 💡 우리 프로젝트의 실제 데이터는 GET이 아니라 **POST**로 받아옵니다(레슨 03).
> 왜 POST인지는 다음 레슨에서 "사이트가 데이터를 어떻게 주는지" 관찰하며 알게 됩니다.

➡ 다음: [02_inspect_site](../02_inspect_site/README.md)
