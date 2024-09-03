from enum import Enum
from unittest.mock import patch

import pytest

from acslib.ccure.base import CcureACS, CcureConnection
from acslib.ccure import CcureAPI
from acslib.ccure.filters import PersonnelFilter


def test_default_ccure_acs(env_config, caplog):
    """Default picks up env vars."""
    ccure = CcureACS(connection=None)
    assert ccure.config.base_url == "https://example.com/ccure"
    assert ccure.logger.name == "acslib.ccure.connection"
    assert "acslib.ccure.connection" in caplog.text


def test_user_supplied_logger(env_config, caplog):
    """."""
    import logging

    cc_conn = CcureConnection(logger=logging.getLogger("test"))
    ccure = CcureACS(connection=cc_conn)
    assert ccure.logger.name == "test"
    assert "test:connection" in caplog.text


def test_ccure_personnel_search(env_config, personnel_response, ccure_connection, caplog):
    ccure = CcureAPI(ccure_connection)
    search_filter = PersonnelFilter(display_properties=["ObjectID", "FirstName"])
    with patch("acslib.ccure.base.CcureACS.search", return_value=personnel_response) as mock_search:
        ccure.personnel.search(terms=["test"], search_filter=search_filter)
        mock_search.assert_called_with(
            object_type="SoftwareHouse.NextGen.Common.SecurityObjects.Personnel",
            search_filter=search_filter,
            terms=["test"],
            page_size=None,
            page_number=1,
            timeout=0,
            search_options=None,
            where_clause=None,
        )
    assert "Searching for personnel" in caplog.text


@pytest.mark.skip(reason="ccure search no longer works this way")
def test_invalid_search_type(env_config):
    class NewTypes(Enum):
        NEW = "new"
        PERSONNEL = "personnel"

    ccure = CcureACS()
    with pytest.raises(ValueError):
        ccure.search(search_type=NewTypes.NEW, terms=["test"])
