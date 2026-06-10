"""변하기 쉬운 KOFIA 지식을 한 곳에 (레슨 07: '변경 국소화')."""
from pathlib import Path

URL = "https://dis.kofia.or.kr/proframeWeb/XMLSERVICES/"   # ← 대문자 W!
HEADERS = {"Content-Type": "application/xml; charset=UTF-8", "User-Agent": "Mozilla/5.0"}

# 학습용 DB는 학습 폴더 안에 (team_learning/playground.db)
DB = Path(__file__).resolve().parent.parent / "playground.db"

# 응답 <selectMeta> 안 tmpV 위치 → 의미 (KOFIA가 바뀌면 여기만 고치면 됨)
COL = {
    "company": "tmpV1",   # 운용사
    "name":    "tmpV2",   # 펀드명
    "type":    "tmpV3",   # 펀드유형
    "aum":     "tmpV5",   # 설정액(백만원)
    "nav":     "tmpV6",   # 기준가(원)
    "code":    "tmpV12",  # 펀드코드(표준코드)
    "date":    "tmpV14",  # 기준일자
}

TDF_KEYWORDS = ("TDF", "TARGET DATE", "타겟데이트", "타깃데이트")

# 자주 쓰는 운용사 코드(tmpV11). 빈값=전체(느림).
COMPANIES = {"교보악사": "A01015", "삼성": "A01005", "미래에셋": "A01048"}
