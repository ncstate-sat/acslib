from enum import Enum
from unittest.mock import patch

import pytest

from acslib.ccure.base import CcureACS, CcureConnection
from acslib.ccure.filters import PersonnelFilter, SearchTypes


def test_default_ccure_acs(env_config, caplog):
    """Default picks up env vars."""
    ccure = CcureACS()
    assert ccure.config.base_url == "https://example.com/ccure"
    assert ccure.logger.name == "acslib.ccure.base"
    assert "acslib.ccure.base" in caplog.text


def test_user_supplied_logger(env_config, caplog):
    """."""
    import logging

    cc_conn = CcureConnection(logger=logging.getLogger("test"))
    ccure = CcureACS(connection=cc_conn)
    assert ccure.logger.name == "test"
    assert "test:base" in caplog.text


def test_default_ccure_search(env_config, personnel_response, caplog):
    ccure = CcureACS()
    with patch(
        "acslib.ccure.base.CcureACS._search_people", return_value=personnel_response
    ) as mock_search:
        ccure.search(search_type=SearchTypes.PERSONNEL, terms=["test"])
        mock_search.assert_called_with(["test"])
    assert "Searching for personnel" in caplog.text


def test_ccure_search_with_filter(env_config, personnel_response, caplog):
    ccure = CcureACS()
    filter = PersonnelFilter()
    with patch(
        "acslib.ccure.base.CcureACS._search_people", return_value=personnel_response
    ) as mock_search:
        ccure.search(search_type=SearchTypes.PERSONNEL, terms=["test"], search_filter=filter)
        mock_search.assert_called_with(["test"], filter)
    assert "Searching for personnel" in caplog.text


def test_invalid_search_type(env_config):
    class NewTypes(Enum):
        NEW = "new"
        PERSONNEL = "personnel"

    ccure = CcureACS()
    with pytest.raises(ValueError):
        ccure.search(search_type=NewTypes.NEW, terms=["test"])
