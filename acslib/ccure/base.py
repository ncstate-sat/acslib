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
from acslib.ccure.search import PersonnelFilter, ClearanceFilter


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


class CcureAPI:
    def __init__(self, connection: Optional[CcureConnection] = None):
        self.personnel = CCurePersonnel(connection)
        self.clearance = CCureClearance(connection)
        self.credential = CCureCredential(connection)


class CcureACS(AccessControlSystem):
    """."""

    def __init__(self, connection: Optional[CcureConnection] = None):
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

    # def _search_people(self, terms: list, search_filter: Optional[ACSFilter] = None) -> ACSRequestResponse:
    #     if not search_filter:
    #         search_filter = PersonnelFilter()
    #     request_json = {
    #         "TypeFullName": "Personnel",
    #         "DisplayProperties": search_filter.display_properties,
    #         "pageSize": self.connection.config.page_size,
    #         "pageNumber": 1,
    #         "WhereClause": search_filter.filter(terms),
    #     }
    #     if not search_filter.display_properties:
    #         del request_json["DisplayProperties"]

    #     return self.connection.request(
    #         ACSRequestMethod.POST,
    #         request_data=ACSRequestData(
    #             url=self.connection.config.base_url
    #             + self.connection.config.endpoints.FIND_OBJS_W_CRITERIA,
    #             request_json=request_json,
    #             headers=self.connection.headers,
    #         ),
    #     )

    # def _search_clearances(self, terms: list, search_filter: Optional[ACSFilter] = None) -> ACSRequestResponse:
    #     if not search_filter:
    #         search_filter = ClearanceFilter()
    #     request_json = {
    #         "partitionList": [],
    #         "propertyList": search_filter.display_properties,
    #         "pageSize": self.connection.config.page_size,
    #         "pageNumber": 1,
    #         "whereClause": search_filter.filter(terms),
    #         "sortColumnName": "",
    #         "whereArgList": [],
    #         "explicitPropertyList": [],
    #     }
    #     if not search_filter.display_properties:
    #         del request_json["DisplayProperties"]

    #     response = self.connection.request(
    #         ACSRequestMethod.POST,
    #         request_data=ACSRequestData(
    #             url=self.connection.config.base_url
    #             + self.connection.config.endpoints.CLEARANCES_FOR_ASSIGNMENT,
    #             request_json=request_json,
    #             headers=self.connection.headers,
    #         ),
    #     )
    #     if response.json:
    #         response.json = response.json[1:]

    #     return response


class CCurePersonnel(CcureACS):
    def __init__(self, connection: Optional[CcureConnection] = None):
        super().__init__(connection)
        self.request_options = {
            "TypeFullName": "Personnel",
            "pageSize": self.connection.config.page_size,
            "pageNumber": 1,
        }
        self.search_filter = PersonnelFilter()

    def search(self, terms: list, search_filter: PersonnelFilter = None) -> ACSRequestResponse:
        self.logger.info("Searching for personnel")
        if search_filter:
            self.search_filter = search_filter
        request_json = {
            "DisplayProperties": self.search_filter.display_properties,
            "WhereClause": self.search_filter.filter(terms),
        }
        request_json.update(self.request_options)
        if not self.search_filter.display_properties:
            del request_json["DisplayProperties"]

        return self.connection.request(
            ACSRequestMethod.POST,
            request_data=ACSRequestData(
                url=self.config.base_url + self.config.endpoints.FIND_OBJS_W_CRITERIA,
                request_json=request_json,
                headers=self.connection.headers,
            ),
        ).json

    def count(self) -> int:
        self.request_options["pageSize"] = 0
        self.request_options["CountOnly"] = True
        self.request_options["WhereClause"] = ""
        return self.connection.request(
            ACSRequestMethod.POST,
            request_data=ACSRequestData(
                url=self.config.base_url + self.config.endpoints.FIND_OBJS_W_CRITERIA,
                request_json=self.request_options,
                headers=self.connection.headers,
            ),
        ).json

    def update(self, record_id: str, update_data: dict) -> ACSRequestResponse:
        pass

    def create(self, create_data: dict) -> ACSRequestResponse:
        pass

    def delete(self, record_id: str) -> ACSRequestResponse:
        pass


class CCureClearance(CcureACS):
    def __init__(self, connection: Optional[CcureConnection] = None):
        super().__init__(connection)
        self.request_options = {
            "partitionList": [],
            "pageSize": self.connection.config.page_size,
            "pageNumber": 1,
            "sortColumnName": "",
            "whereArgList": [],
            "propertyList": ["Name"],
            "explicitPropertyList": [],
        }
        self.search_filter = ClearanceFilter()

    def search(self, terms: str, search_filter: ClearanceFilter = None) -> ACSRequestResponse:
        self.logger.info("Searching for clearances")
        if search_filter:
            self.search_filter = search_filter
        request_json = {
            "whereClause": self.search_filter.filter(terms),
        }
        request_json.update(self.request_options)
        return self.connection.request(
            ACSRequestMethod.POST,
            request_data=ACSRequestData(
                url=self.connection.config.base_url
                + self.connection.config.endpoints.CLEARANCES_FOR_ASSIGNMENT,
                request_json=request_json,
                headers=self.connection.headers,
            ),
        ).json[1:]

    def count(self) -> int:
        request_options = {}
        request_options["TypeFullName"] = "Clearance"
        request_options["pageSize"] = 0
        request_options["pageNumber"] = 1
        request_options["CountOnly"] = True
        request_options["WhereClause"] = ""

        return self.connection.request(
            ACSRequestMethod.POST,
            request_data=ACSRequestData(
                url=self.config.base_url + self.config.endpoints.FIND_OBJS_W_CRITERIA,
                request_json=request_options,
                headers=self.connection.headers,
            ),
        ).json

    def update(self, record_id: str, update_data: dict) -> ACSRequestResponse:
        pass

    def create(self, create_data: dict) -> ACSRequestResponse:
        pass

    def delete(self, record_id: str) -> ACSRequestResponse:
        pass


class CCureCredential(CcureACS):
    def __init__(self, connection: Optional[CcureConnection] = None):
        super().__init__(connection)
        self.request_options = {
            "partitionList": [],
            "pageSize": self.connection.config.page_size,
            "pageNumber": 1,
            "sortColumnName": "",
            "whereArgList": [],
            "propertyList": ["Name"],
            "explicitPropertyList": [],
        }

    def search(self, terms: Optional[list[int]] = None) -> ACSRequestResponse:
        self.logger.info("Searching for credentials")
        if terms:
            # return credentials associated with all given personnel
            result = []
            for person_object_id in terms:
                response = self.connection.request(
                    ACSRequestMethod.POST,
                    request_data=ACSRequestData(
                        url=self.connection.config.base_url
                        + self.connection.config.endpoints.FIND_OBJS_W_CRITERIA,
                        request_json={
                            "TypeFullName": "SoftwareHouse.NextGen.Common.SecurityObjects.Credential",
                            "pageSize": 100,
                            "pageNumber": 1,
                            "WhereClause": f"PersonnelID = {person_object_id}"
                        },
                        headers=self.connection.headers
                    )
                )
                result.extend(response.json)
            return result
        else:
            # return all credentials
            return self.connection.request(
                ACSRequestMethod.GET,
                request_data=ACSRequestData(
                    url=self.connection.config.base_url
                    + self.connection.config.endpoints.GET_CREDENTIALS,
                    headers=self.connection.headers
                )
            ).json[1:]

    def count(self) -> int:
        response = self.connection.request(
            ACSRequestMethod.GET,
            request_data=ACSRequestData(
                url=self.config.base_url + self.config.endpoints.GET_CREDENTIALS,
                headers=self.connection.headers
            ),
        ).json
        return response[0]["TotalRowsInAllPages"]

    def update(self, record_id: str, update_data: dict) -> ACSRequestResponse:
        pass

    def create(self, create_data: dict) -> ACSRequestResponse:
        pass

    def delete(self, record_id: int) -> ACSRequestResponse:
        # NOTE This hasn't been tested yet. Don't test until we know how to make new credentials
        return self.connection.request(
            ACSRequestMethod.DELETE,
            request_data=ACSRequestData(
                url = self.config.base_url
                + self.config.endpoints.DELETE_CREDENTIAL.format(_id=record_id),
                headers=self.connection.headers
            )
        )
