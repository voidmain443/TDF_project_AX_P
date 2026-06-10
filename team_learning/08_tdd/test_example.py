"""레슨 08: pytest 첫 테스트. '순수 함수'를 네트워크 없이 검증한다.

실행:  python -m pytest team_learning/08_tdd/test_example.py -v
"""


# ── 시험 대상: 작은 순수 함수 (실제 parsers.parse_number의 축소판) ──
def parse_number(s):
    """'1,927.46' -> 1927.46 ; '' / '-' / None -> None"""
    if s is None:
        return None
    s = s.strip().replace(",", "")
    if s in ("", "-"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


# ── 테스트: test_ 로 시작하는 함수 + assert ──────────────────────
def test_보통_숫자():
    assert parse_number("1,927.46") == 1927.46


def test_앞에_점만():
    # KOFIA 보수 값은 '.24' 처럼 0이 생략돼 오기도 한다
    assert parse_number(".24") == 0.24


def test_빈_값과_대시는_None():
    assert parse_number("") is None
    assert parse_number("-") is None
    assert parse_number(None) is None


# pytest 없이 그냥 실행해도 결과를 보여주도록(학습 편의)
if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"PASSED  {name}")
    print("\n모든 테스트 통과! (정식으로는: python -m pytest 이 파일 -v)")
