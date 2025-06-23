import logging
from numbers import Number
from typing import Optional

from acslib.base import (
    ACSConnection,
    ACSRequestData,
    ACSRequestException,
    ACSRequestResponse,
    status,
)
from acslib.base.connection import ACSRequestMethod
from acslib.ccure.config import CcureConfigFactory


class CcureConnection(ACSConnection):
    def __init__(self, **kwargs):
        """
        A connection object to the CCure Server.
        Parameters:
        :param kwargs:
        """
        self._session_id = None
        if conn_logger := kwargs.get("logger"):
            self.logger = conn_logger
        else:
            self.logger = logging.getLogger(__name__)

        if not kwargs.get("config"):
            kwargs["config"] = CcureConfigFactory()
        self.logger.info("Initializing CCure connection")
        super().__init__(**kwargs)

    @property
    def session_id(self) -> str:
        if self._session_id:
            return self._session_id
        return self.login()

    @property
    def base_headers(self):
        """Headers required for each request to CCure"""
        return {
            "session-id": self.session_id,
            "Access-Control-Expose-Headers": "session-id",
        }

    @property
    def header_for_form_data(self):
        return {"Content-Type": "application/x-www-form-urlencoded"}

    def login(self):
        """Open a new CCure session and generate a new session ID"""
        try:
            response = self.request(
                ACSRequestMethod.POST,
                request_data=ACSRequestData(
                    url=self.config.base_url + self.config.endpoints.LOGIN,
                    data=self.config.connection_data,
                ),
            )
            self._session_id = response.headers["session-id"]
            self.logger.debug(f"Fetched new Session ID: {self._session_id}")
        except ACSRequestException as e:
            self.logger.error(f"Error Fetching Session ID: {e}")
            self.log_session_details()
            self.logger.debug(f"Connection data: {self.config.connection_data}")
            raise e
        return self._session_id

    def logout(self):
        """Log out of the CCure session"""
        if self._session_id:
            self.logger.debug(f"Logging out of CCure session: {self._session_id}")
            try:
                self.request(
                    ACSRequestMethod.POST,
                    request_data=ACSRequestData(
                        url=self.config.base_url + self.config.endpoints.LOGOUT,
                        headers={"session-id": self._session_id},
                    ),
                )
            except ACSRequestException as e:
                self.logger.error(f"Error logging out of CCure session: {e}")
                self.log_session_details()
            finally:
                self.logger.debug(f"Removing Session ID: {self._session_id}")
                self._session_id = None

    def keepalive(self):
        """Prevent the CCure api session from expiring from inactivity"""
        self.logger.debug(f"Keeeping CCure session alive: {self.session_id}")
        try:
            self.request(
                ACSRequestMethod.POST,
                request_data=ACSRequestData(
                    url=self.config.base_url + self.config.endpoints.KEEPALIVE,
                    headers={
                        "session-id": self.session_id,
                        "Access-Control-Expose-Headers": "session-id",
                    },
                ),
            )
            self.logger.debug(f"Session kept alive: {self.session_id}")
        except ACSRequestException as e:
            self.logger.error(f"Error keeping CCure session alive: {e}")
            self.log_session_details()
            self.logout()

    def request(
        self,
        requests_method: ACSRequestMethod,
        request_data: ACSRequestData,
        timeout: Optional[Number] = 0,
        request_attempts: int = 2,
    ) -> ACSRequestResponse:
        """
        Call the `ACSConnection.handle_requests` function and return the result.
        If the response is a 401, get a new CCure session_id and try the request again.

        Parameters:
            requests_method: A method from the requests module. get, post, etc
            request_data: Data used as kwargs for the requests_method
            timeout: Maximum time to wait for a server response, in seconds
            request_attempts: Maximum number of times to try the request

        Returns: An object with status_code, json, and headers attributes
        """
        while request_attempts > 0:
            try:
                return super().request(
                    requests_method,
                    request_data,
                    timeout or self.config.timeout,
                )
            except ACSRequestException as e:
                if e.status_code != status.HTTP_401_UNAUTHORIZED or request_attempts == 1:
                    raise e
                request_attempts -= 1
                self.logout()
                request_data.headers["session-id"] = self.session_id

    def log_session_details(self):
        """Log session ID and the api version number"""
        version_url = self.config.base_url + self.config.endpoints.VERSIONS
        self.logger.error(f"Session ID: {self._session_id}")
        try:
            response = self.request(
                ACSRequestMethod.POST,
                request_data=ACSRequestData(url=version_url),
            ).json
            self.logger.debug(f"CCure webservice version: {response.get('webServiceVersion')}")
            self.logger.debug(f"CCure app server version: {response.get('appServerVersion')}")
        except ACSRequestException as e:
            self.logger.debug(f"Could not get CCure api version number: {e}")

    @staticmethod
    def encode_data(data: dict) -> str:
        """
        Encode a dictionary of form data as a string for requests

        Parameters:
            data: form data for the request

        Returns: the string of encoded data
        """

        def get_form_entries(data: dict, prefix: str = "") -> list[str]:
            """
            Convert the data dict into a list of form entries

            Parameters:
                data: data about the new clearance assignment

            Returns: list of strings representing key/value pairs
            """
            entries = []
            for key, val in data.items():
                if isinstance(val, (int, float, str)):
                    if prefix:
                        entries.append(f"{prefix}[{key}]={val}")
                    else:
                        entries.append(f"{key}={val}")
                elif isinstance(val, (list, tuple)):
                    for i, list_item in enumerate(val):
                        if isinstance(list_item, dict):
                            entries.extend(
                                get_form_entries(data=list_item, prefix=prefix + f"{key}[{i}]")
                            )
                        elif prefix:
                            entries.append(f"{prefix}[{key}][]={list_item}")
                        else:
                            entries.append(f"{key}[]={list_item}")
            return entries

        return "&".join(get_form_entries(data))
