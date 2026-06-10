"""TDD: Proframe envelope builder + HTTP fetcher retry behaviour."""

import pytest
import requests

from tdf_crawler import config
from tdf_crawler.fetchers import get_fetcher, HttpFetcher
from tdf_crawler.fetchers.base import build_envelope


def test_build_envelope_contains_header_and_params():
    spec = config.SERVICES["stdprice"]
    body = build_envelope(spec, {"tmpV30": "20260604", "tmpV11": ""}).decode()
    assert "<pfmSvcName>DISFundStdPriceSO</pfmSvcName>" in body
    assert "<DISCondFuncDTO>" in body
    assert "<tmpV30>20260604</tmpV30>" in body
    assert "<tmpV11></tmpV11>" in body


def test_build_envelope_escapes_special_chars():
    spec = config.SERVICES["stdprice"]
    body = build_envelope(spec, {"q": "a&b<c"}).decode()
    assert "a&amp;b&lt;c" in body


class _Resp:
    def __init__(self, content=b"<ok/>", status=200):
        self.content = content
        self._status = status

    def raise_for_status(self):
        if self._status >= 400:
            raise requests.HTTPError(f"status {self._status}")


class _Session:
    """Fails `fail_times` then succeeds, recording attempts."""

    def __init__(self, fail_times=0):
        self.fail_times = fail_times
        self.attempts = 0

    def post(self, url, data, headers, timeout):
        self.attempts += 1
        if self.attempts <= self.fail_times:
            raise requests.ConnectionError("boom")
        return _Resp(b"<ok/>")


def test_http_fetcher_retries_then_succeeds(monkeypatch):
    monkeypatch.setattr("tdf_crawler.fetchers.http_fetcher.time.sleep", lambda *_: None)
    sess = _Session(fail_times=2)
    f = HttpFetcher(session=sess, max_retries=3)
    out = f.fetch(config.SERVICES["stdprice"], {"tmpV30": "20260604"})
    assert out == b"<ok/>"
    assert sess.attempts == 3


def test_http_fetcher_raises_after_exhausting_retries(monkeypatch):
    monkeypatch.setattr("tdf_crawler.fetchers.http_fetcher.time.sleep", lambda *_: None)
    sess = _Session(fail_times=99)
    f = HttpFetcher(session=sess, max_retries=2)
    with pytest.raises(RuntimeError):
        f.fetch(config.SERVICES["stdprice"], {})


def test_get_fetcher_unknown_source():
    with pytest.raises(ValueError):
        get_fetcher("carrier-pigeon")
