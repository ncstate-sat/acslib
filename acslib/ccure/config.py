import os
from acslib.ccure.endpoints import V2Endpoints


class CcureConfig:

    def __init__(self, **kwargs):
        self.page_size = kwargs.get("PAGE_SIZE", 100)
        self.clearance_limit = kwargs.get("CLEARANCE_LIMIT", 40)
        self.timeout = kwargs.get("TIMEOUT", 3)
        self.endpoints = None

    USERNAME = os.getenv("CCURE_USERNAME")
    PASSWORD = os.getenv("CCURE_PASSWORD")
    BASE_URL = os.getenv("CCURE_BASE_URL")
    CLIENT_NAME = os.getenv("CCURE_CLIENT_NAME")
    CLIENT_VERSION = os.getenv("CCURE_CLIENT_VERSION")
    CLIENT_ID = os.getenv("CCURE_CLIENT_ID")

    @property
    def connection_data(self):
        return {
            "UserName": self.USERNAME,
            "Password": self.PASSWORD,
            "ClientName": self.CLIENT_NAME,
            "ClientVersion": self.CLIENT_VERSION,
            "ClientID": self.CLIENT_ID,
        }


class CcureConfigFactory:

    def __new__(cls, *args, **kwargs) -> CcureConfig:
        api_version = kwargs.get("api_version", 2)
        instance = CcureConfig(**kwargs)
        if api_version == 2:
            instance.endpoints = V2Endpoints
        else:
            raise ValueError(f"Invalid API version: {api_version}")
        return instance
