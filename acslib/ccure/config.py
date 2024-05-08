import os

from acslib.base.config import ACSConfig, ACSConfigException
from acslib.ccure.endpoints import V2Endpoints


class CcureConfig(ACSConfig):
    """
    CcureConfig returns an object that implements the ACSConfig interface.
    It expects the following variables to be set either in the environment or passed as kwargs:
        CCURE_USERNAME
        CCURE_PASSWORD
        CCURE_BASE_URL
        CCURE_CLIENT_NAME
        CCURE_CLIENT_VERSION
        CCURE_CLIENT_ID
    :param PAGE_SIZE: default 100
    :param CLEARANCE_LIMIT: default 40
    :param TIMEOUT: default 3
    :param kwargs:
    :return: CcureConfig
    """

    def __init__(self, **kwargs):
        self.page_size = kwargs.get("page_size", 100)
        self.current_page = 1
        self.clearance_limit = kwargs.get("clearance_limit", 40)
        self.timeout = kwargs.get("timeout", 3)
        self.endpoints = None
        self.username = kwargs.get("CCURE_USERNAME", os.getenv("CCURE_USERNAME"))
        self.password = kwargs.get("CCURE_PASSWORD", os.getenv("CCURE_PASSWORD"))
        self.base_url = kwargs.get("CCURE_BASE_URL", os.getenv("CCURE_BASE_URL"))
        self.client_name = kwargs.get("CCURE_CLIENT_NAME", os.getenv("CCURE_CLIENT_NAME"))
        self.client_version = kwargs.get("CCURE_CLIENT_VERSION", os.getenv("CCURE_CLIENT_VERSION"))
        self.client_id = kwargs.get("CCURE_CLIENT_ID", os.getenv("CCURE_CLIENT_ID"))
        if not all(
            [
                self.username,
                self.password,
                self.base_url,
                self.client_name,
                self.client_version,
                self.client_id,
            ]
        ):
            raise ACSConfigException(
                "Missing required environment variables: "
                "CCURE_USERNAME, CCURE_PASSWORD, CCURE_BASE_URL, CCURE_CLIENT_NAME, "
                "CCURE_CLIENT_VERSION, CCURE_CLIENT_ID"
            )

    def __str__(self):
        return self.client_version

    @property
    def connection_data(self) -> dict:
        return {
            "UserName": self.username,
            "Password": self.password,
            "ClientName": self.client_name,
            "ClientVersion": self.client_version,
            "ClientID": self.client_id,
        }


class CcureConfigFactory:
    def __new__(cls, *args, **kwargs) -> CcureConfig:
        """
        CcuureConfigFactory returns a CcureConfig instance with the correct endpoints for the requested API version.
        The default api version is 2.
        :param args:
        :param kwargs:
        :return: CcureConfig
        """
        api_version = kwargs.get("api_version", 2)
        instance = CcureConfig(**kwargs)
        match api_version:
            case 2:
                instance.endpoints = V2Endpoints
            case _:
                raise ACSConfigException(f"Invalid API version: {api_version}")
        return instance
