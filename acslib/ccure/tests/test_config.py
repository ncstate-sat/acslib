import os

import pytest

from acslib.base import ACSConfigException
from acslib.ccure.config import CcureConfigFactory


def test_ccure_config_with_kwargs(config):
    """."""
    assert config.base_url == "https://example.com/ccure"
    assert config.connection_data == {
        "UserName": "test",
        "Password": "test",
        "ClientName": "test",
        "ClientVersion": "test",
        "ClientID": "test",
    }
    assert config.base_url == "https://example.com/ccure"
    assert str(config) == "test"
    assert config.page_size == 100
    assert config.clearance_limit == 40
    assert config.timeout == 3


def test_ccure_config_with_env_vars():
    """."""
    os.environ = {
        "CCURE_USERNAME": "test",
        "CCURE_PASSWORD": "test",
        "CCURE_BASE_URL": "https://example.com/ccure",
        "CCURE_CLIENT_NAME": "test",
        "CCURE_CLIENT_VERSION": "test",
        "CCURE_CLIENT_ID": "test",
    }
    config = CcureConfigFactory()
    assert config.connection_data == {
        "UserName": "test",
        "Password": "test",
        "ClientName": "test",
        "ClientVersion": "test",
        "ClientID": "test",
    }
    assert config.base_url == "https://example.com/ccure"
    assert str(config) == "test"
    assert config.page_size == 100
    assert config.clearance_limit == 40
    assert config.timeout == 3


def test_ccure_config_change_page_size():
    config = CcureConfigFactory(page_size=200)
    assert config.page_size == 200


def test_ccure_config_change_clearance_limit():
    config = CcureConfigFactory(clearance_limit=50)
    assert config.clearance_limit == 50


def test_ccure_config_change_timeout():
    config = CcureConfigFactory(timeout=5)
    assert config.timeout == 5


def test_no_ccure_connection_vars():
    """."""
    os.environ = {}
    with pytest.raises(ACSConfigException) as e:
        CcureConfigFactory()
    assert "Missing required environment variables" in str(e.value)


def test_missing_ccure_connection_vars():
    """."""
    os.environ = {
        "CCURE_USERNAME": "test",
        "CCURE_PASSWORD": "test",
        "CCURE_BASE_URL": "https://example.com/ccure",
        "CCURE_CLIENT_NAME": "test",
    }
    with pytest.raises(ACSConfigException) as e:
        CcureConfigFactory()
    assert "Missing required environment variables" in str(e.value)


def test_unsupported_api_version():
    """."""
    os.environ = {
        "CCURE_USERNAME": "test",
        "CCURE_PASSWORD": "test",
        "CCURE_BASE_URL": "https://example.com/ccure",
        "CCURE_CLIENT_NAME": "test",
        "CCURE_CLIENT_VERSION": "test",
        "CCURE_CLIENT_ID": "test",
    }
    with pytest.raises(ACSConfigException) as e:
        CcureConfigFactory(api_version=3)
    assert "Invalid API version: 3" in str(e.value)
