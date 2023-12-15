import json
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Optional

import requests
from pydantic import BaseModel, Field

from acslib.base import status


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


class ACSRequestMethod(Enum):
    GET = "get"
    POST = "post"
    PUT = "put"
    DELETE = "delete"
    PATCH = "patch"


class ACSRequestResponse:
    """Successful queries from handle_request return this type of object"""

    def __init__(
        self, status_code: int, json: Any, headers: requests.structures.CaseInsensitiveDict
    ):
        self.status_code = status_code
        self.json = json
        self.headers = headers

    def count(self):
        return len(self.json)


class ACSRequestData(BaseModel):
    """Kwargs used in requests get/post/etc methods"""

    url: str
    headers: Optional[dict] = {}
    data: Optional[dict] = {}
    json: Optional[dict] = Field(alias="json", default=json.loads("{}"))


class ACSConnection(ABC):
    REQUEST_TYPE = {
        ACSRequestMethod.GET: requests.get,
        ACSRequestMethod.POST: requests.post,
        ACSRequestMethod.PUT: requests.put,
        ACSRequestMethod.DELETE: requests.delete,
        ACSRequestMethod.PATCH: requests.patch,
    }

    def __init__(self, **kwargs):
        self.config = kwargs.get("config")
        self.timeout = kwargs.get("timeout", 1)
        self.response = None

    @abstractmethod
    def login(self):
        pass

    @abstractmethod
    def logout(self):
        pass

    @staticmethod
    def _encode_data(data: dict) -> str:
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
                if isinstance(val, (int, str)):
                    if prefix:
                        entries.append(f"{prefix}[{key}]={val}")
                    else:
                        entries.append(f"{key}={val}")
                elif isinstance(val, list):
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

    def _make_request(self, requests_method: ACSRequestMethod, request_data_map: dict):
        if req := self.REQUEST_TYPE.get(requests_method):
            return req(**request_data_map, timeout=self.timeout)
        raise ACSConnectionException(f"Invalid request method: {requests_method}")

    def request(
        self, requests_method: ACSRequestMethod, request_data: ACSRequestData
    ) -> ACSRequestResponse:
        """
        Process requests to remote servers.
        Either return a response with the resulting status code, json data, and headers,
        or raise an exception with the appropriate status code

        Parameters:
            requests_method: A method from the requests module. requests.get, requests.post, etc
            request_data: Data used as kwargs for the requests_method
            timeout: Maximum time to wait for a server response, in seconds

        Returns: An object with status_code, json, and headers attributes
        """

        try:
            request_data_map = request_data.model_dump()
            request_data_map["data"] = self._encode_data(request_data_map.get("data", {}))
            response = self._make_request(requests_method, request_data_map)
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
                log_message=f"Unable to connect to remote server in {self.timeout} second(s)",
            )
        except requests.ReadTimeout:
            # The server did not send any data in the allotted amount of time.
            raise ACSRequestException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                log_message=f"No response from remote server in {self.timeout} second(s)",
            )
        except requests.Timeout:
            # The request timed out.
            # Watching this error will catch both ConnectTimeout and ReadTimeout errors.
            raise ACSRequestException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                log_message=f"Request took longer than {self.timeout} second(s)",
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
