"""Fetchers turn a (ServiceSpec, params) request into raw response bytes."""

from .base import Fetcher, build_envelope
from .http_fetcher import HttpFetcher

__all__ = ["Fetcher", "build_envelope", "HttpFetcher", "get_fetcher"]


def get_fetcher(source: str = "http", **kwargs) -> Fetcher:
    """Factory: 'http' (default) or 'selenium' (optional dependency)."""
    if source == "http":
        return HttpFetcher(**kwargs)
    if source == "selenium":
        from .selenium_fetcher import SeleniumFetcher  # lazy: optional dep
        return SeleniumFetcher(**kwargs)
    raise ValueError(f"unknown fetcher source: {source!r}")
