from typing import Optional, Any

from acslib.base import AccessControlSystem, ACSRequestData, ACSRequestResponse, ACSRequestException
from acslib.ccure.connection import CcureConnection, ACSRequestMethod
from acslib.ccure.filters import CcureFilter, NFUZZ, PersonnelFilter


class CcureACS(AccessControlSystem):
    """Base class for CCure API interactions"""

    def __init__(self, connection: Optional[CcureConnection]):
        if not connection:
            connection = CcureConnection()
        super().__init__(connection=connection)
        self.logger = self.connection.logger
        self.request_options = {}

    @property
    def config(self):
        """Return the ccure connection configuration"""
        return self.connection.config

    def search(
        self,
        object_type: str,
        terms: Optional[list] = None,
        search_filter: Optional[CcureFilter] = None,
        page_size: Optional[int] = None,
        page_number: int = 1,
        timeout: float = 0,
        search_options: Optional[dict] = None,
        where_clause: Optional[str] = None,
    ) -> int | list:
        """
        Return CCure objects meeting the given criteria

        object_type: full name of the CCure object type, such as those in ObjectType
        search_filter: CcureFilter object specifying search query and display properties
        terms: search terms used to filter objects. Leave empty to include everything in results
        page_size: number of search results to include
                     - defaults to the page_size value in acslib/ccure/config.py
        page_number: the page of search results to display. The first page is page 1.
        search_options: other options to include in the request_json. eg. "CountOnly"
        where_clause: sql-style WHERE clause to search objects. overrides `terms` if included.
        """
        if search_filter is None and not where_clause:
            raise ACSRequestException(400, "A search filter or where clause is required.")
        if page_size is None:
            page_size = self.config.page_size
        request_json = {
            "TypeFullName": object_type,
            "pageSize": page_size,
            "pageNumber": page_number,
            "DisplayProperties": search_filter.display_properties,
            "WhereClause": where_clause or search_filter.filter(terms or []),
        } | (search_options or {})
        response = self.connection.request(
            ACSRequestMethod.POST,
            request_data=ACSRequestData(
                url=self.connection.config.base_url
                + self.connection.config.endpoints.FIND_OBJS_W_CRITERIA,
                request_json=request_json,
                headers=self.connection.base_headers,
            ),
            timeout=timeout,
        )
        return response.json

    def search_personnel(
        self,
        search_filter: PersonnelFilter,
        sort_column: str,
        terms: Optional[list] = None,
        page_size: Optional[int] = None,
        page_number: int = 1,
        timeout: float = 0,
        search_options: Optional[dict] = None,
        where_clause: Optional[str] = None,
        where_arg_list: Optional[list[str]] = None,
    ) -> list[dict]:
        """
        Personnel requires a separate endpoint to support searching with special characters
        """
        is_valid_search = search_filter and terms or where_clause and where_arg_list
        if search_filter is None and not (where_clause and where_arg_list):
            raise ACSRequestException(400, "A search filter or where clause is required.")
        if not terms and not (where_clause and where_arg_list):
            raise ACSRequestException(
                400,
                "where_clause and where_arg_list are required if search terms are not included.",
            )
        if not is_valid_search:
            where_clause, where_arg_list = search_filter.filter(terms or [])
        if page_size is None:
            page_size = self.config.page_size
        request_json = {
            "pageSize": page_size,
            "pageNumber": page_number,
            "propertyList": search_filter.display_properties,
            "explicitPropertyList": search_filter.explicit_property_list,
            "sortColumnName": sort_column,
            "whereClause": where_clause,
            "whereArgList": where_arg_list,
        } | (search_options or {})
        response = self.connection.request(
            ACSRequestMethod.POST,
            request_data=ACSRequestData(
                url=self.connection.config.base_url
                + self.connection.config.endpoints.PERSONNEL_SEARCH,
                request_json=request_json,
                headers=self.connection.base_headers,
            ),
            timeout=timeout,
        )
        return response.json[1:]

    def get_property(self, object_type: str, object_id: int, property_name: str) -> Any:
        """Return the value of one property from one CCure object"""
        search_filter = CcureFilter(lookups={"ObjectID": NFUZZ}, display_properties=[property_name])
        response = CcureACS.search(
            self,
            object_type=object_type,
            terms=[object_id],
            search_filter=search_filter,
            page_size=1,
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
        Edit the properties of one CCure object

        update_data: maps property names to their new values
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
        """Persist a new CCure object"""
        return self.connection.request(
            ACSRequestMethod.POST,
            request_data=ACSRequestData(
                url=self.config.base_url + self.config.endpoints.PERSIST_TO_CONTAINER,
                data=self.connection.encode_data(request_data),
                headers=self.connection.base_headers | self.connection.header_for_form_data,
            ),
        )

    def add_children(
        self, parent_type: str, parent_id: int, child_type: str, child_configs: list[dict]
    ) -> ACSRequestResponse:
        """Persist a new CCure object as a child of an existing CCure object"""
        request_data = {
            "type": parent_type,
            "ID": parent_id,
            "Children": [
                {
                    "Type": child_type,
                    "PropertyNames": list(child_config.keys()),
                    "Propertyvalues": list(child_config.values()),
                }
                for child_config in child_configs
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

    def remove_children(
        self, parent_type: str, parent_id: int, child_type: str, child_ids: list[int]
    ) -> ACSRequestResponse:
        """Remove child CCure objects from a parent CCure object"""
        request_data = {
            "type": parent_type,
            "ID": parent_id,
            "Children": [
                {
                    "Type": child_type,
                    "ID": child_id,
                }
                for child_id in child_ids
            ],
        }
        return self.connection.request(
            ACSRequestMethod.POST,
            request_data=ACSRequestData(
                url=self.config.base_url + self.config.endpoints.REMOVE_FROM_CONTAINER,
                data=self.connection.encode_data(request_data),
                headers=self.connection.base_headers | self.connection.header_for_form_data,
            ),
        )

    def delete(self, object_type: str, object_id: int) -> ACSRequestResponse:
        """Delete a CCure object"""
        return self.connection.request(
            ACSRequestMethod.DELETE,
            request_data=ACSRequestData(
                url=self.config.base_url + self.config.endpoints.DELETE_OBJECT,
                params={"type": object_type, "id": object_id},
                headers=self.connection.base_headers,
            ),
        )
