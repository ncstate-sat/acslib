import os
from acslib.ccure.endpoints import V2Endpoints
from acslib.base import ACSConfig, ACSConfigException


class CcureConfig(ACSConfig):
    def __init__(self, **kwargs):
        self.page_size = kwargs.get("PAGE_SIZE", 100)
        self.clearance_limit = kwargs.get("CLEARANCE_LIMIT", 40)
        self.timeout = kwargs.get("TIMEOUT", 3)
        self.endpoints = None
        self.username = os.getenv("CCURE_USERNAME")
        self.password = os.getenv("CCURE_PASSWORD")
        self.base_url = os.getenv("CCURE_BASE_URL")
        self.client_name = os.getenv("CCURE_CLIENT_NAME")
        self.client_version = os.getenv("CCURE_CLIENT_VERSION")
        self.client_id = os.getenv("CCURE_CLIENT_ID")

    @property
    def connection_data(self):
        return {
            "UserName": self.username,
            "Password": self.password,
            "ClientName": self.client_name,
            "ClientVersion": self.client_version,
            "ClientID": self.client_id,
        }


class CcureConfigFactory:
    def __new__(cls, *args, **kwargs) -> CcureConfig:
        api_version = kwargs.get("api_version", 2)
        instance = CcureConfig(**kwargs)
        if api_version == 2:
            instance.endpoints = V2Endpoints
        else:
            raise ACSConfigException(f"Invalid API version: {api_version}")
        return instance
