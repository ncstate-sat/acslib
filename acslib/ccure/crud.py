from typing import Optional

from acslib.base import ACSRequestData, ACSRequestResponse
from acslib.base.connection import ACSRequestMethod
from acslib.ccure.base import CcureACS
from acslib.ccure.connection import CcureConnection
from acslib.ccure.search import PersonnelFilter, ClearanceFilter, CredentialFilter


class CcureAPI:
    def __init__(self, connection: Optional[CcureConnection] = None):
        self.personnel = CCurePersonnel(connection)
        self.clearance = CCureClearance(connection)
        self.credential = CCureCredential(connection)


class CCurePersonnel(CcureACS):
    def __init__(self, connection: Optional[CcureConnection] = None):
        super().__init__(connection)
        self.search_filter = PersonnelFilter()

    def search(self, terms: list, search_filter: Optional[PersonnelFilter] = None) -> ACSRequestResponse:
        self.logger.info("Searching for personnel")
        search_filter = search_filter or self.search_filter
        request_json = {
            "TypeFullName": "Personnel",
            "pageSize": self.connection.config.page_size,
            "pageNumber": 1,
            "DisplayProperties": search_filter.display_properties,
            "WhereClause": search_filter.filter(terms)
        }

        return self.connection.request(
            ACSRequestMethod.POST,
            request_data=ACSRequestData(
                url=self.config.base_url + self.config.endpoints.FIND_OBJS_W_CRITERIA,
                request_json=request_json,
                headers=self.connection.headers,
            ),
        ).json

    def count(self) -> int:
        request_json = {
            "TypeFullName": "Personnel",
            "pageSize": 0,
            "CountOnly": True,
            "WhereClause": ""
        }
        return self.connection.request(
            ACSRequestMethod.POST,
            request_data=ACSRequestData(
                url=self.config.base_url + self.config.endpoints.FIND_OBJS_W_CRITERIA,
                request_json=request_json,
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
        self.search_filter = ClearanceFilter()

    def search(self, terms: list, search_filter: Optional[ClearanceFilter] = None) -> ACSRequestResponse:
        self.logger.info("Searching for clearances")
        search_filter = search_filter or self.search_filter
        request_json = {
            "partitionList": [],
            "pageSize": self.connection.config.page_size,
            "pageNumber": 1,
            "sortColumnName": "",
            "whereArgList": [],
            "explicitPropertyList": [],
            "propertyList": search_filter.display_properties,
            "whereClause": search_filter.filter(terms)
        }
        return self.connection.request(
            ACSRequestMethod.POST,
            request_data=ACSRequestData(
                url=self.connection.config.base_url
                + self.connection.config.endpoints.CLEARANCES_FOR_ASSIGNMENT,
                request_json=request_json,
                headers=self.connection.headers
            ),
        ).json[1:]

    def count(self) -> int:
        request_options = {
            "pageSize": 0,
            "TypeFullName": "Clearance",
            "pageNumber": 1,
            "CountOnly": True,
            "WhereClause": ""
        }
        return self.connection.request(
            ACSRequestMethod.POST,
            request_data=ACSRequestData(
                url=self.config.base_url + self.config.endpoints.FIND_OBJS_W_CRITERIA,
                request_json=request_options,
                headers=self.connection.headers
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
        self.search_filter = CredentialFilter()

    def search(self, terms: Optional[list] = None, search_filter: Optional[CredentialFilter] = None) -> ACSRequestResponse:
        self.logger.info("Searching for credentials")
        if terms:
            search_filter = search_filter or self.search_filter
            request_json = {
                "TypeFullName": "SoftwareHouse.NextGen.Common.SecurityObjects.Credential",
                "pageSize": 100,
                "pageNumber": 1,
                "DisplayProperties": search_filter.display_properties,
                "WhereClause": search_filter.filter(terms)
            }
            response = self.connection.request(
                ACSRequestMethod.POST,
                request_data=ACSRequestData(
                    url=self.connection.config.base_url
                    + self.connection.config.endpoints.FIND_OBJS_W_CRITERIA,
                    request_json=request_json,
                    headers=self.connection.headers
                )
            )
            return response.json
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
        return self.connection.request(
            ACSRequestMethod.DELETE,
            request_data=ACSRequestData(
                url = self.config.base_url
                + self.config.endpoints.DELETE_CREDENTIAL.format(_id=record_id),
                headers=self.connection.headers
            )
        )
