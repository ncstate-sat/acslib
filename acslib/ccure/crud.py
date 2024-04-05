from typing import Optional

from acslib.base import ACSRequestData, ACSRequestResponse
from acslib.base.connection import ACSRequestMethod
from acslib.ccure.base import CcureACS
from acslib.ccure.connection import CcureConnection
from acslib.ccure.filters import (
    ClearanceFilter,
    ClearanceItemFilter,
    CredentialFilter,
    PersonnelFilter,
)
from acslib.ccure.types import ClearanceItemCreateData, ClearanceItemType, CredentialCreateData


class CcureAPI:
    def __init__(self, connection: Optional[CcureConnection] = None):
        self.personnel = CcurePersonnel(connection)
        self.clearance = CcureClearance(connection)
        self.credential = CcureCredential(connection)
        self.clearance_item = CcureClearanceItem(connection)


class CcurePersonnel(CcureACS):
    def __init__(self, connection: Optional[CcureConnection] = None):
        super().__init__(connection)
        self.search_filter = PersonnelFilter()

    def search(self, terms: list, search_filter: Optional[PersonnelFilter] = None) -> list:
        self.logger.info("Searching for personnel")
        search_filter = search_filter or self.search_filter
        request_json = {
            "TypeFullName": "Personnel",
            "pageSize": self.connection.config.page_size,
            "pageNumber": 1,
            "DisplayProperties": search_filter.display_properties,
            "WhereClause": search_filter.filter(terms),
        }

        return self.connection.request(
            ACSRequestMethod.POST,
            request_data=ACSRequestData(
                url=self.config.base_url + self.config.endpoints.FIND_OBJS_W_CRITERIA,
                request_json=request_json,
                headers=self.connection.base_headers,
            ),
        ).json

    def count(self) -> int:
        request_json = {
            "TypeFullName": "Personnel",
            "pageSize": 0,
            "CountOnly": True,
            "WhereClause": "",
        }
        return self.connection.request(
            ACSRequestMethod.POST,
            request_data=ACSRequestData(
                url=self.config.base_url + self.config.endpoints.FIND_OBJS_W_CRITERIA,
                request_json=request_json,
                headers=self.connection.base_headers,
            ),
        ).json

    def update(self, record_id: str, update_data: dict) -> ACSRequestResponse:
        pass

    def create(self, create_data: dict) -> ACSRequestResponse:
        pass

    def delete(self, record_id: str) -> ACSRequestResponse:
        pass


class CcureClearance(CcureACS):
    def __init__(self, connection: Optional[CcureConnection] = None):
        super().__init__(connection)
        self.search_filter = ClearanceFilter()

    def search(self, terms: list, search_filter: Optional[ClearanceFilter] = None) -> list:
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
            "whereClause": search_filter.filter(terms),
        }
        return self.connection.request(
            ACSRequestMethod.POST,
            request_data=ACSRequestData(
                url=self.connection.config.base_url
                + self.connection.config.endpoints.CLEARANCES_FOR_ASSIGNMENT,
                request_json=request_json,
                headers=self.connection.base_headers,
            ),
        ).json[1:]

    def count(self) -> int:
        request_options = {
            "pageSize": 0,
            "TypeFullName": "Clearance",
            "pageNumber": 1,
            "CountOnly": True,
            "WhereClause": "",
        }
        return self.connection.request(
            ACSRequestMethod.POST,
            request_data=ACSRequestData(
                url=self.config.base_url + self.config.endpoints.FIND_OBJS_W_CRITERIA,
                request_json=request_options,
                headers=self.connection.base_headers,
            ),
        ).json

    def update(self, record_id: str, update_data: dict) -> ACSRequestResponse:
        pass

    def create(self, create_data: dict) -> ACSRequestResponse:
        pass

    def delete(self, record_id: str) -> ACSRequestResponse:
        pass


class CcureCredential(CcureACS):
    def __init__(self, connection: Optional[CcureConnection] = None):
        super().__init__(connection)
        self.search_filter = CredentialFilter()

    def search(
        self, terms: Optional[list] = None, search_filter: Optional[CredentialFilter] = None
    ) -> list:
        self.logger.info("Searching for credentials")
        if terms:
            search_filter = search_filter or self.search_filter
            request_json = {
                "TypeFullName": "SoftwareHouse.NextGen.Common.SecurityObjects.Credential",
                "pageSize": 100,
                "pageNumber": 1,
                "DisplayProperties": search_filter.display_properties,
                "WhereClause": search_filter.filter(terms),
            }
            response = self.connection.request(
                ACSRequestMethod.POST,
                request_data=ACSRequestData(
                    url=self.connection.config.base_url
                    + self.connection.config.endpoints.FIND_OBJS_W_CRITERIA,
                    request_json=request_json,
                    headers=self.connection.base_headers,
                ),
            )
            return response.json
        else:
            # return all credentials
            return self.connection.request(
                ACSRequestMethod.GET,
                request_data=ACSRequestData(
                    url=self.connection.config.base_url
                    + self.connection.config.endpoints.GET_CREDENTIALS,
                    headers=self.connection.base_headers,
                ),
            ).json[1:]

    def count(self) -> int:
        response = self.connection.request(
            ACSRequestMethod.GET,
            request_data=ACSRequestData(
                url=self.config.base_url + self.config.endpoints.GET_CREDENTIALS,
                headers=self.connection.base_headers,
            ),
        ).json
        return response[0]["TotalRowsInAllPages"]

    def update(self, record_id: str, update_data: dict) -> ACSRequestResponse:
        return self.connection.request(
            ACSRequestMethod.PUT,
            request_data=ACSRequestData(
                url=self.config.base_url + self.config.endpoints.EDIT_OBJECT,
                params={
                    "type": "SoftwareHouse.NextGen.Common.SecurityObjects.Credential",
                    "id": record_id,
                },
                data=self.connection.encode_data(
                    {
                        "PropertyNames": list(update_data.keys()),
                        "PropertyValues": list(update_data.values()),
                    }
                ),
                headers=self.connection.base_headers | self.connection.header_for_form_data,
            ),
        )

    def create(self, personnel_id: int, create_data: CredentialCreateData) -> ACSRequestResponse:
        """
        Create a new credential object associated with a personnel object

        create_data properties:
            - `CHUID` is required.
            - `Name` has no effect on the new credential object.
            - `FacilityCode` defaults to 0.
            - If `CardNumber` isn't present in create_data, CHUID will be saved as 0 regardless
            of the `CHUID` value in create_data.
        """
        create_data_dict = create_data.model_dump()
        request_data = {
            "type": "SoftwareHouse.NextGen.Common.SecurityObjects.Personnel",
            "ID": personnel_id,
            "Children": [
                {
                    "Type": "SoftwareHouse.NextGen.Common.SecurityObjects.Credential",
                    "PropertyNames": list(create_data_dict.keys()),
                    "PropertyValues": list(create_data_dict.values()),
                }
            ],
        }
        return self.connection.request(
            ACSRequestMethod.POST,
            request_data=ACSRequestData(
                url=self.config.base_url + self.config.endpoints.PERSIST_TO_CONTAINER,
                data=self.connection.encode_data(request_data),
                headers=self.connection.base_headers | self.connection.header_for_form_data,
            ),
        )

    def delete(self, record_id: int) -> ACSRequestResponse:
        return self.connection.request(
            ACSRequestMethod.DELETE,
            request_data=ACSRequestData(
                url=self.config.base_url
                + self.config.endpoints.DELETE_CREDENTIAL.format(_id=record_id),
                headers=self.connection.base_headers,
            ),
        )


class CcureClearanceItem(CcureACS):
    def __init__(self, connection: Optional[CcureConnection] = None):
        super().__init__(connection)
        self.search_filter = ClearanceItemFilter()

    def search(
        self,
        item_type: ClearanceItemType,
        terms: Optional[list] = None,
        search_filter: Optional[ClearanceItemFilter] = None,
    ) -> list:
        self.logger.info("Searching for clearance items")
        search_filter = search_filter or self.search_filter
        request_json = {
            "TypeFullName": item_type.complete,
            "pageSize": 100,
            "pageNumber": 1,
            "DisplayProperties": search_filter.display_properties,
            "WhereClause": search_filter.filter(terms),
        }
        response = self.connection.request(
            ACSRequestMethod.POST,
            request_data=ACSRequestData(
                url=self.connection.config.base_url
                + self.connection.config.endpoints.GET_ALL_WITH_CRITERIA,
                request_json=request_json,
                headers=self.connection.base_headers,
            ),
        )
        return response.json

    def count(self, item_type: ClearanceItemType) -> int:
        request_json = {
            "TypeFullName": item_type.complete,
            "pageSize": 0,
            "CountOnly": True,
            "WhereClause": "",
        }
        response = self.connection.request(
            ACSRequestMethod.POST,
            request_data=ACSRequestData(
                url=self.connection.config.base_url
                + self.connection.config.endpoints.GET_ALL_WITH_CRITERIA,
                request_json=request_json,
                headers=self.connection.base_headers,
            ),
        )
        return response.json

    def update(
        self, item_type: ClearanceItemType, item_id: str, update_data: dict
    ) -> ACSRequestResponse:
        return self.connection.request(
            ACSRequestMethod.PUT,
            request_data=ACSRequestData(
                url=self.config.base_url + self.config.endpoints.EDIT_OBJECT,
                params={"type": item_type.complete, "id": item_id},
                data=self.connection.encode_data(
                    {
                        "PropertyNames": list(update_data.keys()),
                        "PropertyValues": list(update_data.values()),
                    }
                ),
                headers=self.connection.base_headers | self.connection.header_for_form_data,
            ),
        )

    def create(
        self,
        item_type: ClearanceItemType,
        controller_id: int,
        create_data: ClearanceItemCreateData,
    ) -> ACSRequestResponse:
        """
        Create a new clearance item object

        :param item_type: eg ClearanceItemType.DOOR, ClearanceItemType.ELEVATOR
        :param controller_id: object ID for the iStarController object for the new clearance item
        :param create_data: object with properties required to create a new clearance item
        """
        create_data_dict = create_data.model_dump()
        request_data = {
            "type": "SoftwareHouse.NextGen.Common.SecurityObjects.iStarController",
            "ID": controller_id,
            "Children": [
                {
                    "Type": item_type.complete,
                    "PropertyNames": list(create_data_dict.keys()),
                    "PropertyValues": list(create_data_dict.values()),
                }
            ],
        }
        return self.connection.request(
            ACSRequestMethod.POST,
            request_data=ACSRequestData(
                url=self.config.base_url + self.config.endpoints.PERSIST_TO_CONTAINER,
                data=self.connection.encode_data(request_data),
                headers=self.connection.base_headers | self.connection.header_for_form_data,
            ),
        )

    def delete(self, item_type: ClearanceItemType, item_id: int) -> ACSRequestResponse:
        return self.connection.request(
            ACSRequestMethod.DELETE,
            request_data=ACSRequestData(
                url=self.config.base_url + self.config.endpoints.DELETE_OBJECT,
                params={"type": item_type.complete, "id": item_id},
                headers=self.connection.base_headers,
            ),
        )
