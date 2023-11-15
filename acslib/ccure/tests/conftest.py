import random
from dataclasses import dataclass, field

import pytest
from faker import Faker

from acslib.ccure.base import CcureConnection
from acslib.ccure.config import CcureConfigFactory

fake = Faker()

BASE_CONFIG = {
    "CCURE_USERNAME": "test",
    "CCURE_PASSWORD": "test",
    "CCURE_BASE_URL": "https://example.com/ccure",
    "CCURE_CLIENT_NAME": "test",
    "CCURE_CLIENT_VERSION": "test",
    "CCURE_CLIENT_ID": "test",
}


@dataclass
class MockResponse:
    status_code: int = 200
    _json: dict = field(default_factory=dict)
    _headers: dict = field(default_factory=dict)
    text: str = ""

    def json(self):
        return self._json

    @property
    def headers(self):
        return self._headers


@pytest.fixture
def env_config(monkeypatch):
    for k, v in BASE_CONFIG.items():
        monkeypatch.setenv(k, v)


@pytest.fixture
def config():
    """."""
    return CcureConfigFactory(api_version=2, **BASE_CONFIG)


@pytest.fixture
def ccure_connection(config):
    """."""
    return CcureConnection(config=config)


@pytest.fixture
def base_mock_response():
    """."""

    def _mock_response(json=None, headers=None, text="", status_code=200):
        return MockResponse(
            **{
                "_json": json if json else {},
                "_headers": headers if headers else {},
                "text": text,
                "status_code": status_code,
            }
        )

    return _mock_response


@pytest.fixture
def response_w_session(base_mock_response):
    Faker.seed(random.randint(0, 10000))
    return base_mock_response(headers={"session-id": fake.lexify("session-?????????????????")})


@pytest.fixture
def personnel_response(response_w_session):
    response_w_session._json = {"FirstName": "Test", "MiddleName": "Ng", "LastName": "Stuff"}
    return response_w_session
