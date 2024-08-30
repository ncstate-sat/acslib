from unittest.mock import patch

import pytest
import requests

from acslib.base import ACSRequestException


def test_ccure_connection(ccure_connection, response_w_session):
    """."""
    with patch(
        "acslib.base.connection.ACSConnection._make_request", return_value=response_w_session
    ):
        session_id = ccure_connection.login()
    assert session_id == ccure_connection.session_id


@pytest.mark.parametrize(
    "side_effect",
    [
        requests.URLRequired,
        requests.HTTPError,
        requests.TooManyRedirects,
        requests.ConnectTimeout,
        requests.ReadTimeout,
        requests.Timeout,
        requests.ConnectionError,
        requests.RequestException,
    ],
)
def test_failed_login(ccure_connection, response_w_session, side_effect):
    with patch("acslib.base.connection.ACSConnection._make_request", side_effect=side_effect):
        with pytest.raises(ACSRequestException):
            ccure_connection.login()


def test_internal_server_error(ccure_connection, response_w_session):
    from acslib.base import status

    response_w_session.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    with patch(
        "acslib.base.connection.ACSConnection._make_request", return_value=response_w_session
    ):
        with pytest.raises(ACSRequestException):
            ccure_connection.login()


def test_unhandled_request_error(ccure_connection, response_w_session):
    from acslib.base import status

    response_w_session.status_code = status.HTTP_421_MISDIRECTED_REQUEST
    with patch(
        "acslib.base.connection.ACSConnection._make_request", return_value=response_w_session
    ):
        with pytest.raises(ACSRequestException):
            ccure_connection.login()


def test_ccure_logout(ccure_connection, response_w_session):
    with patch(
        "acslib.base.connection.ACSConnection._make_request", return_value=response_w_session
    ):
        session_id = ccure_connection.login()
        assert ccure_connection._session_id == session_id
        ccure_connection.logout()
        assert ccure_connection._session_id is None
