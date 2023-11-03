from abc import ABC, abstractmethod
from typing import Iterable, Any, Callable, Optional

import requests
from acslib.base import status
from pydantic import BaseModel, Field


class ACSConnectionException(Exception):
    pass


class ACSRequestException(Exception):
    """
    Exception raised on a failed request, including exceptions
    from the requests module and 400+ status codes
    """

    def __init__(self, status_code: int, log_message: str):
        self.status_code = status_code
        self.message = log_message

    def __str__(self):
        return f"RequestException: {self.status_code} {self.message}"


class ACSRequestResponse:
    """Successful queries from handle_request return this type of object"""

    def __init__(
        self, status_code: int, json: Any, headers: requests.structures.CaseInsensitiveDict
    ):
        self.status_code = status_code
        self.json = json
        self.headers = headers


class ACSRequestData(BaseModel):
    """Kwargs used in requests get/post/etc methods"""

    url: str
    data: Optional[dict | str]
    headers: Optional[dict]
    request_json: Optional[dict] = Field(alias="json")


class ACSConnection(ABC):

    def __init__(self, **kwargs):
        self.config = kwargs.get("config")
        self.timeout = kwargs.get("timeout", 1)
        self.session_id = None

    @abstractmethod
    def login(self):
        if not self.config:
            raise ACSConnectionException("No config provided")
        pass

    @abstractmethod
    def logout(self):
        pass

    def handle_request(
        self, requests_method: Callable, request_data: ACSRequestData
    ) -> ACSRequestResponse:
        """
        Process requests to remote servers.
        Either return a response with the resulting status code, json data, and headers,
        or raise an exception with the appropriate status code

        Parameters:
            requests_method: A method from the requests module. get, post, etc
            request_data: Data used as kwargs for the requests_method
            timeout: Maximum time to wait for a server response, in seconds

        Returns: An object with status_code, json, and headers attributes
        """
        try:
            request_data_map = request_data.model_dump()
            request_data_map["json"] = request_data_map.pop("request_json")
            response = requests_method(**request_data_map, timeout=self.timeout)
        except requests.HTTPError:
            # An HTTP error occurred.
            raise ACSRequestException(
                status_code=status.HTTP_400_BAD_REQUEST,
                log_message="An error occurred with this request",
            )

        except requests.URLRequired:
            # A valid URL is required to make a request.
            raise ACSRequestException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                log_message="A valid URL wasn't provided for this request",
            )

        except requests.TooManyRedirects:
            # Too many redirects.
            raise ACSRequestException(
                status_code=status.HTTP_421_MISDIRECTED_REQUEST, log_message="Too many redirects"
            )

        except requests.ConnectTimeout:
            # The request timed out while trying to connect to the remote server.
            # Requests that produced this error are safe to retry.
            raise ACSRequestException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                log_message=f"Unable to connect to remote server in {timeout} second(s)",
            )

        except requests.ReadTimeout:
            # The server did not send any data in the allotted amount of time.
            raise ACSRequestException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                log_message=f"No response from remote server in {timeout} second(s)",
            )

        except requests.Timeout:
            # The request timed out.
            # Watching this error will catch both ConnectTimeout and ReadTimeout errors.
            raise ACSRequestException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                log_message=f"Request took longer than {timeout} second(s)",
            )

        except requests.ConnectionError:
            # A Connection error occurred.
            raise ACSRequestException(
                status_code=status.HTTP_400_BAD_REQUEST,
                log_message="Could not connect to the remote host",
            )

        except requests.RequestException:
            # There was an ambiguous exception that occurred while handling your request.
            raise ACSRequestException(
                status_code=status.HTTP_400_BAD_REQUEST,
                log_message="An exception occurred while handling this request",
            )

        if response.status_code in range(200, 300):
            return ACSRequestResponse(
                status_code=response.status_code, json=response.json(), headers=response.headers
            )
        if response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            raise ACSRequestException(
                status_code=status.HTTP_400_BAD_REQUEST, log_message=response.text
            )
        raise ACSRequestException(status_code=response.status_code, log_message=response.text)


class AccessControlSystem(ABC):
    """
    Base class for access control systems
    Not all methods will be used in all implementations
    """

    # Abstract ACS methods

    @abstractmethod
    def search_clearances(self, request_data: dict) -> list:
        """Base method for searching clearances"""

    @abstractmethod
    def get_clearances_count(self) -> int:
        """ "Base method for getting a count of all clearances in the system"""

    @abstractmethod
    def get_assigned_clearances(self, assignee_id) -> list:
        """Base method to get clearances assigned to a person"""

    @abstractmethod
    def get_clearance_by_id(self, clearance_id) -> dict:
        """Base method to get one clearance"""
        # TODO fold this into search_clearances?

    @abstractmethod
    def get_clearances_by_id(self, clearance_ids: list) -> list[dict]:
        """Base method to get multiple clearanaces"""
        # TODO fold this into search_clearances?

    @abstractmethod
    def get_clearance_name(self, clearance_id) -> str:
        """Base method to get a clearance's name"""
        # TODO fold this into search_clearances?

    @abstractmethod
    def get_clearance_names(self, clearance_id: Iterable) -> str:
        """Base method to get clearances' names"""
        # TODO fold this into search_clearances?

    # @abstractmethod
    # @classmethod
    # def assign_clearances(cls, configs: list[dict]):
    #     """Base method to assign one or more clearances to one or more people"""

    # @abstractmethod
    # @classmethod
    # def revoke_clearances(cls, configs: list[dict]):
    #     """Base method to revoke one or more clearances to one or more people"""

    # @abstractmethod
    # @classmethod
    # def disable_person(cls, person_id):
    #     """Base method to set a disable flag on a person's record"""

    # @abstractmethod
    # @classmethod
    # def add_person(cls, property_names, property_values):
    #     """Base method to add a person to the database"""
    #     # TODO refactor. Args should be one dict, not two parallel lists

    @abstractmethod
    def get_clearance_assignees(self, clearance_ids, *args, **kwargs):
        """Base method to get lists of people assigned to the given clearances"""
