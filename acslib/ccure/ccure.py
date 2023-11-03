from typing import Iterable, Callable
import logging
from numbers import Number
from fastapi import status
import requests

from acslib.base import (
    AccessControlSystem,
    ACSConnection,
    ACSRequestException,
    ACSRequestResponse,
    ACSRequestData,
)
from acslib.ccure.config import CcureConfigFactory


logger = logging.getLogger(__name__)


class CcureConnection(ACSConnection):
    """."""

    def __init__(self, **kwargs):
        """."""
        super().__init__(**kwargs)
        if con_logger := kwargs.get("logger"):
            self.logger = con_logger
        else:
            self.logger = logger
        self.config = kwargs.get("config", CcureConfigFactory())

    def login(self):
        """."""
        try:
            response = self.handle_request(
                requests.post,
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
                self.handle_request(
                    requests.post,
                    request_data=ACSRequestData(
                        url=self.config.BASE_URL + self.config.endpoints.LOGOUT,
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
        Runs every minute in the scheduler.
        """
        self.logger.debug(f"Keeeping CCure session alive: {self.session_id}")
        try:
            self.handle_request(
                requests.post,
                request_data=ACSRequestData(
                    url=self.config.BASE_URL + self.config.endpoints.KEEPALIVE,
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

    def handle_request(
        self,
        requests_method: Callable,
        request_data: ACSRequestData,
        timeout: Number = 0,
        request_attempts: int = 2,
    ) -> RequestResponse:
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
        if timeout == 0:
            timeout = self.config.TIMEOUT
        while request_attempts > 0:
            try:
                return super().handle_request(requests_method, request_data, timeout)
            except ACSRequestException as e:
                if e.status_code != status.HTTP_401_UNAUTHORIZED or request_attempts == 1:
                    raise e
                request_attempts -= 1
                self.logout()
                request_data.headers["session-id"] = self.get_session_id()

    def log_session_details(self):
        """Log session ID and the api version number"""
        version_url = self.config.BASE_URL + self.config.endpoints.VERSIONS
        self.logger.error(f"Session ID: {self.session_id}")
        try:
            response = self.handle_request(
                requests.post,
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
        self.connection = CcureConnection(connection=connection)

    def search_clearances(self, request_data: dict) -> list:
        """Method for searching clearances"""

    def get_clearances_count(self) -> int:
        """ "Method for getting a count of all clearances in the system"""

    def get_assigned_clearances(self, assignee_id) -> list:
        """Method to get clearances assigned to a person"""

    def get_clearance_by_id(self, clearance_id) -> dict:
        """Method to get one clearance"""

    def get_clearances_by_id(self, clearance_ids: list) -> list[dict]:
        """Method to get multiple clearanaces"""

    def get_clearance_name(self, clearance_id) -> str:
        """Method to get a clearance's name"""

    def get_clearance_names(self, clearance_id: Iterable) -> str:
        """Method to get clearances' names"""

    # def assign_clearances(cls, configs: list[dict]):
    #     """Method to assign one or more clearances to one or more people"""

    # def revoke_clearances(cls, configs: list[dict]):
    #     """Method to revoke one or more clearances to one or more people"""

    # def disable_person(cls, person_id):
    #     """Method to set a disable flag on a person's record"""

    # def add_person(cls, property_names, property_values):
    #     """Method to add a person to the database"""
    #     # TODO refactor. Args should be one dict, not two parallel lists

    def get_clearance_assignees(self, clearance_ids, *args, **kwargs):
        """Method to get lists of people assigned to the given clearances"""
