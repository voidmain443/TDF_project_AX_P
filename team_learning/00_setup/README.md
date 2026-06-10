# 00. 환경 준비

크롤링 코드를 돌리려면 파이썬과 라이브러리 몇 개가 필요합니다. 5분이면 됩니다.

## 1. 파이썬 확인
```powershell
python --version      # 3.10 이상이면 OK
```
없으면 https://www.python.org 에서 설치(설치 시 "Add to PATH" 체크).

## 2. (선택) 가상환경 만들기
프로젝트별로 라이브러리를 따로 담는 "상자"입니다. 안 만들어도 학습은 가능하지만 습관 들이면 좋아요.
```powershell
python -m venv .venv
.\.venv\Scripts\activate     # 리눅스/맥: source .venv/bin/activate
```

## 3. 라이브러리 설치
```powershell
pip install requests    # 인터넷에서 데이터 받아오기 (레슨 01~06)
pip install pytest      # 테스트 (레슨 08)
```

## 4. 잘 됐는지 확인
```powershell
python -c "import requests, sqlite3, xml.etree.ElementTree; print('준비 완료!')"
```
`준비 완료!` 가 보이면 성공. (`sqlite3`와 `xml`은 파이썬에 기본 내장이라 설치 불필요)

## 무엇을 배웠나
- **pip**으로 외부 라이브러리를 설치한다.
- `requests`(인터넷), `sqlite3`(저장), `xml`(파싱)이 우리가 쓸 3대 도구다.
- 이 중 `sqlite3`·`xml`은 파이썬에 **이미 들어있다**(그래서 이 프로젝트는 의존성이 매우 적다).

➡ 다음: [01_http_basics](../01_http_basics/README.md)
