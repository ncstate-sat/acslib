from dataclasses import dataclass
import os
from typing import Iterable, Callable
from numbers import Number

from fastapi import status
import requests

from .acs_base import AccessControlSystem, ACSConnection
# from .constants import *
from .handle_requests import (
    RequestData,
    RequestException,
    RequestResponse,
    handle_request,
)


class CcureConfig:

    @dataclass
    class Endpoints:
        FIND_OBJS_W_CRITERIA = "/victorwebservice/api/Objects/FindObjsWithCriteriaFilter"
        CLEARANCES_FOR_ASSIGNMENT = "/victorwebservice/api/v2/Personnel/ClearancesForAssignment"
        GET_ALL_WITH_CRITERIA = "/victorwebservice/api/Objects/GetAllWithCriteria"
        PERSIST_TO_CONTAINER = "/victorwebservice/api/Objects/PersistToContainer"
        REMOVE_FROM_CONTAINER = "/victorwebservice/api/Objects/RemoveFromContainer"
        LOGIN = "/victorwebservice/api/Authenticate/Login"
        LOGOUT = "/victorwebservice/api/Authenticate/Logout"
        KEEPALIVE = "/victorwebservice/api/v2/session/keepalive"
        VERSIONS = "/victorwebservice/api/Generic/Versions"
        DISABLE = "/victorwebservice/api/v2/objects/SetProperty"

    USERNAME = os.getenv("CCURE_USERNAME")
    PASSWORD = os.getenv("CCURE_PASSWORD")
    BASE_URL = os.getenv("CCURE_BASE_URL")
    CLIENT_NAME = os.getenv("CCURE_CLIENT_NAME")
    CLIENT_VERSION = os.getenv("CCURE_CLIENT_VERSION")
    CLIENT_ID = os.getenv("CCURE_CLIENT_ID")

    PAGE_SIZE = 100
    CLEARANCE_LIMIT = 40
    TIMEOUT = 3  # seconds


class CcureConnection(ACSConnection):
    """."""
    def __init__(self):
        """."""
        self.session_id = None
        self.scheduled_jobs["minutely_jobs"].append(self.keepalive)

    def login(self):
        """."""
        connection_data = {
                "UserName": CcureConfig.USERNAME,
                "Password": CcureConfig.PASSWORD,
                "ClientName": CcureConfig.CLIENT_NAME,
                "ClientVersion": CcureConfig.CLIENT_VERSION,
                "ClientID": CcureConfig.CLIENT_ID,
            }
        try:
            response = self.handle_request(
                requests.post,
                request_data=RequestData(
                    url=CcureConfig.BASE_URL + CcureConfig.Endpoints.LOGIN,
                    data=connection_data,
                ),
            )
            self.session_id = response.headers["session-id"]
            # logger.debug(f"Fetched new Session ID: {cls.session_id}")
        except RequestException as e:
            # logger.error(f"Error Fetching Session ID: {e}")
            # cls.log_session_details()
            # logger.debug(f"Connection data: {connection_data}")
            raise e
        return self.session_id

    def logout(self):
        """Log out of the CCure session"""
        if self.session_id:
            # logger.debug(f"Logging out of CCure session: {cls.session_id}")
            try:
                self.handle_request(
                    requests.post,
                    request_data=RequestData(
                        url=CcureConfig.BASE_URL + CcureConfig.Endpoints.LOGOUT,
                        headers={"session-id": self.session_id},
                    ),
                )
            except RequestException as e:
                # logger.error(f"Error logging out of CCure session: {e}")
                # cls.log_session_details()
                pass
            finally:
                # logger.debug(f"Removing Session ID: {cls.session_id}")
                self.session_id = None

    def get_session_id(self):
        """."""
        # logger.debug(f"Session ID: {cls.session_id}")
        if self.session_id is None:
            return self.login()
        return self.session_id

    def keepalive(self):
        """
        Prevent the CCure api session from expiring from inactivity.
        Runs every minute in the scheduler.
        """
        # logger.debug(f"Keeeping CCure session alive: {cls.session_id}")
        try:
            self.handle_request(
                requests.post,
                request_data=RequestData(
                    url=CcureConfig.BASE_URL + CcureConfig.Endpoints.KEEPALIVE,
                    headers={
                        "session-id": self.get_session_id(),
                        "Access-Control-Expose-Headers": "session-id",
                    },
                ),
            )
            # logger.debug(f"Session kept alive: {cls.session_id}")
        except RequestException as e:
            # logger.error(f"Error keeping CCure session alive: {e}")
            # cls.log_session_details()
            self.logout()

    def handle_request(
        self,
        requests_method: Callable,
        request_data: RequestData,
        timeout: Number = CcureConfig.TIMEOUT,
        request_attempts: int = 2,
    ) -> RequestResponse:
        """
        Call the `handle_ccure_requests` function and return the result.
        If the response is a 401, get a new CCure session_id and try the request again.

        Parameters:
            requests_method: A method from the requests module. get, post, etc
            request_data: Data used as kwargs for the requests_method
            timeout: Maximum time to wait for a server response, in seconds
            request_attempts: Maximum number of times to retry the request

        Returns: An object with status_code, json, and headers attributes
        """
        while request_attempts > 0:
            try:
                return handle_request(requests_method, request_data, timeout)
            except RequestException as e:
                if e.status_code != status.HTTP_401_UNAUTHORIZED or request_attempts == 1:
                    raise e
                request_attempts -= 1
                self.logout()
                request_data.headers["session-id"] = self.get_session_id()


class CcureACS(AccessControlSystem):
    """."""

    def __init__(self, *args, **kwargs):
        """."""
        self.connection = CcureConnection()

    def search_clearances(request_data: dict) -> list:
        """Method for searching clearances"""

    def get_clearances_count(cls) -> int:
        """"Method for getting a count of all clearances in the system"""

    def get_assigned_clearances(cls, assignee_id) -> list:
        """Method to get clearances assigned to a person"""

    def get_clearance_by_id(cls, clearance_id) -> dict:
        """Method to get one clearance"""

    def get_clearances_by_id(cls, clearance_ids: list) -> list[dict]:
        """Method to get multiple clearanaces"""

    def get_clearance_name(cls, clearance_id) -> str:
        """Method to get a clearance's name"""

    def get_clearance_names(cls, clearance_id: Iterable) -> str:
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

    def get_clearance_assignees(cls, clearance_ids, *args, **kwargs):
        """Method to get lists of people assigned to the given clearances"""
