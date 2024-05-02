from typing import Optional

from acslib.base import AccessControlSystem, ACSRequestData, ACSRequestResponse, ACSRequestException
from acslib.ccure.connection import CcureConnection, ACSRequestMethod
from acslib.ccure.filters import filters_by_type, NFUZZ


class CcureACS(AccessControlSystem):
    """Base class for CCure API interactions"""

    def __init__(self, connection: Optional[CcureConnection] = None):
        """."""
        super().__init__(connection=connection)
        if not self.connection:
            self.connection = CcureConnection()
        self.logger = self.connection.logger
        self.request_options = {}

    @property
    def config(self):
        """."""
        return self.connection.config

    def search(
        self,
        object_type: str,
        terms: Optional[list] = None,
        search_filter=None,
        page_size=100,  # TODO parameterize args
        page_number=1,
        params: dict = {},
    ) -> list:
        """
        doop doop
        """
        search_filter = search_filter or filters_by_type[object_type]
        request_json = {
            "TypeFullName": object_type,
            "pageSize": page_size,
            "pageNumber": page_number,
            "DisplayProperties": search_filter.display_properties,
            "WhereClause": search_filter.filter(terms),
        } | params
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

    def get_property(self, object_type: str, object_id: int, property_name: str):
        """Weeeoooooooo"""
        search_filter = filters_by_type[object_type](
            lookups={"ObjectId": NFUZZ}, display_properties=[property_name]
        )
        response = self.search(
            object_type=object_type, terms=[object_id], search_filter=search_filter, page_size=1
        )
        if response:
            search_result = response[0]
        else:
            return
        if property_name in search_result:
            return search_result[property_name]
        raise ACSRequestException(400, f"CCure object has no `{property_name}` property.")

    def update(self, object_type: str, object_id: int, update_data: dict) -> ACSRequestResponse:
        """
        Honk
        """
        return self.connection.request(
            ACSRequestMethod.PUT,
            request_data=ACSRequestData(
                url=self.config.base_url + self.config.endpoints.EDIT_OBJECT,
                params={
                    "type": object_type,
                    "id": object_id,
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

    def create(self, request_data: dict) -> ACSRequestResponse:
        """
        bluh
        """
        return self.connection.request(
            ACSRequestMethod.POST,
            request_data=ACSRequestData(
                url=self.config.base_url + self.config.endpoints.PERSIST_TO_CONTAINER,
                data=self.connection.encode_data(request_data),
                headers=self.connection.base_headers | self.connection.header_for_form_data,
            ),
        )

    def add_child(
        self, parent_type: str, parent_id: int, child_type: str, child_properties: dict
    ) -> ACSRequestResponse:
        request_data = {
            "type": parent_type,
            "ID": parent_id,
            "Children": [
                {
                    "Type": child_type,
                    "PropertyNames": list(child_properties.keys()),
                    "Propertyvalues": list(child_properties.values()),
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

    def delete(self, object_type: str, object_id: int) -> ACSRequestResponse:
        """Whoooooooop"""
        return self.connection.request(
            ACSRequestMethod.DELETE,
            request_data=ACSRequestData(
                url=self.config.base_url + self.config.endpoints.DELETE_OBJECT,
                params={"type": object_type, "id": object_id},
                headers=self.connection.base_headers,
            ),
        )
