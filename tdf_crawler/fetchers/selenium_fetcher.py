"""Selenium-based fetcher (optional fallback).

Used when the direct HTTP path is blocked or the response structure must be
captured from the live, JS-rendered page. It executes the same Proframe POST
*inside* the browser via ``fetch()`` so it inherits the page's cookies and
headers. Requires the ``selenium`` extra and a Chrome/Chromedriver install.
"""

from __future__ import annotations

import json

from .. import config
from ..config import ServiceSpec
from .base import build_envelope


class SeleniumFetcher:
    def __init__(self, *, url: str = config.XML_GATEWAY, headless: bool = True,
                 driver=None, warmup_url: str = config.BASE_URL):
        self.url = url
        self._external_driver = driver is not None
        self.driver = driver or self._make_driver(headless)
        # Visit the site once so the session has valid cookies.
        self.driver.get(warmup_url)

    @staticmethod
    def _make_driver(headless: bool):
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        opts = Options()
        if headless:
            opts.add_argument("--headless=new")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--no-sandbox")
        return webdriver.Chrome(options=opts)

    def fetch(self, spec: ServiceSpec, params: dict) -> bytes:
        body = build_envelope(spec, params).decode("utf-8")
        script = """
            const done = arguments[arguments.length - 1];
            fetch(arguments[0], {
                method: 'POST',
                headers: {'Content-Type': 'application/xml; charset=UTF-8'},
                body: arguments[1],
            }).then(r => r.text()).then(t => done(t)).catch(e => done('ERR:' + e));
        """
        self.driver.set_script_timeout(config.DEFAULT_TIMEOUT + 10)
        result = self.driver.execute_async_script(script, self.url, body)
        if isinstance(result, str) and result.startswith("ERR:"):
            raise RuntimeError(f"selenium fetch failed: {result[4:]}")
        return result.encode("utf-8")

    def close(self) -> None:
        if not self._external_driver:
            self.driver.quit()
