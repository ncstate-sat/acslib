import logging
from unittest.mock import patch

from acslib.ccure.base import CcureACS, CcureConnection
from acslib.ccure.search import SearchTypes


def test_default_ccure_acs(env_config):
    """Default picks up env vars."""
    ccure = CcureACS()
    assert ccure.config.base_url == "https://example.com/ccure"
    assert ccure.logger.name == "acslib.ccure.base"


def test_user_supplied_logger(env_config):
    """."""
    cc_conn = CcureConnection(logger=logging.getLogger("test"))
    ccure = CcureACS(connection=cc_conn)
    assert ccure.logger.name == "test"


def test_default_ccure_search(env_config, personnel_response):
    ccure = CcureACS()
    with patch("acslib.ccure.base.CcureACS._search_people", return_value=personnel_response):
        ccure.search(search_type=SearchTypes.PERSONNEL, terms=["test"])
