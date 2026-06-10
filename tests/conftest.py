"""Shared test helpers: fixture loader + a canned Fetcher."""

from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def load_fixture():
    def _load(name: str) -> bytes:
        return (FIXTURES / name).read_bytes()
    return _load


class FakeFetcher:
    """Returns canned bytes keyed by Proframe service name; records calls."""

    def __init__(self, responses: dict[str, bytes]):
        self.responses = responses
        self.calls: list[tuple[str, dict]] = []

    def fetch(self, spec, params: dict) -> bytes:
        self.calls.append((spec.service_name, params))
        return self.responses[spec.service_name]


@pytest.fixture
def fake_fetcher():
    from tdf_crawler import config

    def _build(**fixtures: str) -> FakeFetcher:
        # fixtures maps service-key (stdprice/fees) -> fixture filename
        responses = {
            config.SERVICES[key].service_name: (FIXTURES / fname).read_bytes()
            for key, fname in fixtures.items()
        }
        return FakeFetcher(responses)
    return _build
