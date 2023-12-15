import logging
from numbers import Number
from typing import Optional

from acslib.base import (
    AccessControlSystem,
    ACSConnection,
    ACSRequestData,
    ACSRequestException,
    ACSRequestResponse,
    status,
)
from acslib.base.connection import ACSRequestMethod
from acslib.base.search import ACSFilter
from acslib.ccure.config import CcureConfigFactory
from acslib.ccure.search import PersonnelFilter, ClearanceFilter, SearchTypes

logger = logging.getLogger(__name__)


class CcureConnection(ACSConnection):
    def __init__(self, **kwargs):
        """
        A connection object to the CCure Server.
        Parameters:
        :param kwargs:
        """
        self.session_id = None
        if con_logger := kwargs.get("logger"):
            self.logger = con_logger
        else:
            self.logger = logger
        if not kwargs.get("config"):
            kwargs["config"] = CcureConfigFactory()
        self.logger.info("Initializing CCure connection")
        super().__init__(**kwargs)

    @property
    def headers(self):
        """."""
        return {
            "session-id": self.get_session_id(),
            "Access-Control-Expose-Headers": "session-id",
        }

    def login(self):
        """."""
        try:
            response = self.request(
                ACSRequestMethod.POST,
                request_data=ACSRequestData(
                    url=self.config.base_url + self.config.endpoints.LOGIN,
                    data=self.config.connection_data,
                ),
            )
            self.session_id = response.headers["session-id"]
            self.logger.debug(f"Fetched new Session ID: {self.session_id}")
        except ACSRequestException as e:
            self.logger.error(f"Error Fetching Session ID: {e}")
            self.log_session_details()
            self.logger.debug(f"Connection data: {self.config.connection_data}")
            raise e
        return self.session_id

    def logout(self):
        """Log out of the CCure session"""
        if self.session_id:
            self.logger.debug(f"Logging out of CCure session: {self.session_id}")
            try:
                self.request(
                    ACSRequestMethod.POST,
                    request_data=ACSRequestData(
                        url=self.config.base_url + self.config.endpoints.LOGOUT,
                        headers={"session-id": self.session_id},
                    ),
                )
            except ACSRequestException as e:
                self.logger.error(f"Error logging out of CCure session: {e}")
                self.log_session_details()
            finally:
                self.logger.debug(f"Removing Session ID: {self.session_id}")
                self.session_id = None

    def get_session_id(self):
        """."""
        self.logger.debug(f"Session ID: {self.session_id}")
        if self.session_id is None:
            return self.login()
        return self.session_id

    def keepalive(self):
        """
        Prevent the CCure api session from expiring from inactivity.
        """
        self.logger.debug(f"Keeeping CCure session alive: {self.session_id}")
        try:
            self.request(
                ACSRequestMethod.POST,
                request_data=ACSRequestData(
                    url=self.config.base_url + self.config.endpoints.KEEPALIVE,
                    headers={
                        "session-id": self.get_session_id(),
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
        timeout: Number = 0,
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
        # use TIMEOUT as the default timeout value
        if timeout != 0:
            self.config.timeout = timeout
        while request_attempts > 0:
            try:
                return super().request(requests_method, request_data)
            except ACSRequestException as e:
                if e.status_code != status.HTTP_401_UNAUTHORIZED or request_attempts == 1:
                    raise e
                request_attempts -= 1
                self.logout()
                request_data.headers["session-id"] = self.get_session_id()

    def log_session_details(self):
        """Log session ID and the api version number"""
        version_url = self.config.base_url + self.config.endpoints.VERSIONS
        self.logger.error(f"Session ID: {self.session_id}")
        try:
            response = self.request(
                ACSRequestMethod.POST,
                request_data=ACSRequestData(url=version_url),
            ).json
            self.logger.debug(f"CCure webservice version: {response.get('webServiceVersion')}")
            self.logger.debug(f"CCure app server version: {response.get('appServerVersion')}")
        except ACSRequestException as e:
            self.logger.debug(f"Could not get CCure api version number: {e}")


class CcureACS(AccessControlSystem):
    """."""

    def __init__(self, connection: CcureConnection = None):
        """."""
        super().__init__(connection=connection)
        if not self.connection:
            self.connection = CcureConnection()
        self.logger = self.connection.logger
        self.request_options = {}
        self.search_filter = None

    @property
    def config(self):
        """."""
        return self.connection.config

    def _search_people(self, terms: list, search_filter: Optional[ACSFilter] = None) -> ACSRequestResponse:
        if not search_filter:
            search_filter = PersonnelFilter()
        request_json = {
            "TypeFullName": "Personnel",
            "DisplayProperties": search_filter.display_properties,
            "pageSize": self.connection.config.page_size,
            "pageNumber": 1,
            "WhereClause": search_filter.filter(terms),
        }
        if not search_filter.display_properties:
            del request_json["DisplayProperties"]

        return self.connection.request(
            ACSRequestMethod.POST,
            request_data=ACSRequestData(
                url=self.connection.config.base_url
                + self.connection.config.endpoints.FIND_OBJS_W_CRITERIA,
                json=request_json,
                headers=self.connection.headers,
            ),
        )

    def _search_clearances(self, terms: list, search_filter: Optional[ACSFilter] = None) -> ACSRequestResponse:
        if not search_filter:
            search_filter = ClearanceFilter()
        request_json = {
            "partitionList": [],
            "propertyList": search_filter.display_properties,
            "pageSize": self.connection.config.page_size,
            "pageNumber": 1,
            "whereClause": search_filter.filter(terms),
            "sortColumnName": "",
            "whereArgList": [],
            "explicitPropertyList": [],
        }
        if not search_filter.display_properties:
            del request_json["DisplayProperties"]

        return self.connection.request(
            ACSRequestMethod.POST,
            request_data=ACSRequestData(
                url=self.connection.config.base_url
                + self.connection.config.endpoints.CLEARANCES_FOR_ASSIGNMENT,
                json=request_json,
                headers=self.connection.headers,
            ),
        )

    def search(
        self, search_type: SearchTypes, terms: list, search_filter: Optional[ACSFilter] = None
    ) -> ACSRequestResponse:
        match search_type:
            case search_type.PERSONNEL:
                self.logger.info("Searching for personnel")
                return self._search_people(terms, search_filter)
            case search_type.CLEARANCE:
                self.logger.info("Searching for clearances")
                return self._search_clearances(terms, search_filter)
            case _:
                raise ValueError(f"Invalid search type: {search_type}")
