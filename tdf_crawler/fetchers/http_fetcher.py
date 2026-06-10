"""Direct HTTP/XML fetcher (default): POSTs the Proframe envelope via requests."""

from __future__ import annotations

import time

import requests

from .. import config
from ..config import ServiceSpec
from .base import build_envelope


class HttpFetcher:
    def __init__(self, *, url: str = config.XML_GATEWAY, headers: dict | None = None,
                 timeout: int = config.DEFAULT_TIMEOUT, max_retries: int = config.MAX_RETRIES,
                 session: requests.Session | None = None):
        self.url = url
        self.headers = headers or dict(config.DEFAULT_HEADERS)
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = session or requests.Session()

    def fetch(self, spec: ServiceSpec, params: dict) -> bytes:
        body = build_envelope(spec, params)
        last_exc: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                resp = self.session.post(
                    self.url, data=body, headers=self.headers, timeout=self.timeout)
                resp.raise_for_status()
                return resp.content
            except requests.RequestException as exc:  # network / 5xx
                last_exc = exc
                if attempt < self.max_retries:
                    time.sleep(config.RETRY_BACKOFF * attempt)
        raise RuntimeError(
            f"fetch failed after {self.max_retries} attempts for "
            f"{spec.service_name}: {last_exc}") from last_exc
