from acslib.base import ACSRequestResponse
from acslib.base.connection import ACSRequestData, ACSRequestMethod
from acslib.ccure.base import CcureACS
from acslib.ccure.search import ClearanceFilter, PersonnelFilter


class CCurePersonnel(CcureACS):
    def __init__(self, connection):
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
                json=request_json,
                headers=self.connection.headers,
            ),
        )

    def count(self) -> int:
        self.request_options["pageSize"] = 0
        self.request_options["CountOnly"] = True
        self.request_options["WhereClause"] = ""
        return self.connection.request(
            ACSRequestMethod.POST,
            request_data=ACSRequestData(
                url=self.config.base_url + self.config.endpoints.FIND_OBJS_W_CRITERIA,
                json=self.request_options,
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
    def __init__(self, connection):
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
                json=request_json,
                headers=self.connection.headers,
            ),
        )

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
                json=request_options,
                headers=self.connection.headers,
            ),
        ).json

    def update(self, record_id: str, update_data: dict) -> ACSRequestResponse:
        pass

    def create(self, create_data: dict) -> ACSRequestResponse:
        pass

    def delete(self, record_id: str) -> ACSRequestResponse:
        pass
