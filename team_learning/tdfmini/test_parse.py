"""레슨 08: tdfmini.parse 순수함수 테스트 (네트워크 없이).

실행:  cd team_learning  &&  python -m pytest tdfmini/test_parse.py -v
"""
from tdfmini import parse


def test_local_strips_namespace():
    assert parse._local("{http://x}selectMeta") == "selectMeta"


def test_num():
    assert parse._num("1005.23") == 1005.23
    assert parse._num("") is None
    assert parse._num(None) is None


def test_parse_tdf_keeps_only_tdf():
    xml = (b"<root><message>"
           b"<selectMeta><tmpV1>\xea\xb5\x90\xeb\xb3\xb4</tmpV1>"
           b"<tmpV2>KYOBO TDF2045</tmpV2><tmpV12>K1</tmpV12>"
           b"<tmpV14>20260610</tmpV14><tmpV6>1000.5</tmpV6><tmpV5>123</tmpV5></selectMeta>"
           b"<selectMeta><tmpV2>JUST A BOND FUND</tmpV2><tmpV12>K2</tmpV12>"
           b"<tmpV14>20260610</tmpV14></selectMeta>"
           b"</message></root>")
    rows = parse.parse_tdf(xml)
    assert len(rows) == 1                 # TDF만 남음
    assert rows[0]["code"] == "K1"
    assert rows[0]["date"] == "2026-06-10"
    assert rows[0]["nav"] == 1000.5
