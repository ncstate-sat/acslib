from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from acslib.base import ACSRequestResponse, ACSRequestData, ACSRequestException, status
from acslib.base.connection import ACSNotImplementedException
from acslib.ccure.base import CcureACS
from acslib.ccure.connection import CcureConnection, ACSRequestMethod
from acslib.ccure.filters import (
    ClearanceFilter,
    ClearanceItemFilter,
    CredentialFilter,
    GroupFilter,
    GroupMemberFilter,
    JournalFilter,
    PersonnelFilter,
)
from acslib.ccure.data_models import (
    ClearanceItemCreateData,
    CredentialCreateData,
    PersonnelCreateData,
)
from acslib.ccure.types import ObjectType


class CcurePersonnel(CcureACS):
    def __init__(self, connection: CcureConnection):
        super().__init__(connection)
        self.search_filter = PersonnelFilter()
        self.type = ObjectType.PERSONNEL.complete

    def search(
        self,
        terms: Optional[list] = None,
        search_filter: Optional[PersonnelFilter] = None,
        sort_column: str = "LastName",
        page_size: Optional[int] = None,
        page_number: int = 1,
        timeout: float = 0,
        search_options: Optional[dict] = None,
        where_clause: Optional[str] = None,
        where_arg_list: Optional[list[str]] = None,
    ) -> list:
        """
        Get a list of Personnel objects matching given search terms

        :param terms: list of search terms
        :param search_filter: specifies how and in what fields to look for the search terms
        :param where_clause: SQL-style where clause with values replaced with ?
          - eg. "WHERE FirstName = ? and LastName LIKE ?"
          - Values must be provided in the `where_arg_list` argument
        :param where_arg_list: list of values to insert in the `where_clause` string
          - Values must be listed in order
        """
        self.logger.info("Searching for personnel")
        search_filter = search_filter or self.search_filter

        return super().search_personnel(
            terms=terms,
            search_filter=search_filter,
            sort_column=sort_column,
            page_size=page_size,
            page_number=page_number,
            timeout=timeout,
            search_options=search_options,
            where_clause=where_clause,
            where_arg_list=where_arg_list,
        )

    def get_property(self, object_id: int, property_name: str) -> Any:
        return super().get_property(self.type, object_id, property_name)

    def count(
        self, terms: Optional[list] = None, search_filter: Optional[PersonnelFilter] = None
    ) -> int:
        """Get the total number of Personnel objects"""
        search_filter = search_filter or self.search_filter
        return self.search(
            search_filter=search_filter,
            terms=terms,
            search_options={"CountOnly": True},
        )

    def update(self, object_id: int, update_data: dict) -> ACSRequestResponse:
        """
        Edit properties of a personnel object

        :param object_id: the Personnel object's CCure ID
        :param update_data: maps Personnel properties to their new values
        """
        return super().update(object_type=self.type, object_id=object_id, update_data=update_data)

    def create(self, create_data: PersonnelCreateData) -> ACSRequestResponse:
        """
        Create a new personnel object

        create_data must contain a 'LastName' property.
        """
        create_data_dict = create_data.model_dump()
        property_names = list(create_data_dict)
        property_values = list(create_data_dict.values())
        request_data = {
            "Type": self.type,
            "PropertyNames": property_names,
            "PropertyValues": property_values,
        }
        return super().create(request_data=request_data)

    def delete(self, personnel_id: int) -> ACSRequestResponse:
        """Delete a personnel object by its CCure ID"""
        return super().delete(object_type=self.type, object_id=personnel_id)


class CcureClearance(CcureACS):
    def __init__(self, connection: Optional[CcureConnection] = None):
        super().__init__(connection)
        self.search_filter = ClearanceFilter()
        self.type = ObjectType.CLEARANCE.complete

    def search(
        self,
        terms: Optional[list] = None,
        search_filter: Optional[ClearanceFilter] = None,
        page_size: Optional[int] = None,
        page_number: int = 1,
        timeout: float = 0,
        search_options: Optional[dict] = None,
        where_clause: Optional[str] = None,
    ) -> list:
        """
        Get a list of Clearance objects matching given search terms

        :param terms: list of search terms
        :param search filter: specifies how and in what fields to look for the search terms
        """
        self.logger.info("Searching for clearances")
        search_filter = search_filter or self.search_filter
        return super().search(
            object_type=self.type,
            search_filter=search_filter,
            terms=terms,
            page_size=page_size,
            page_number=page_number,
            timeout=timeout,
            search_options=search_options,
            where_clause=where_clause,
        )

    def get_property(self, object_id: int, property_name: str) -> Any:
        return super().get_property(self.type, object_id, property_name)

    def count(
        self, terms: Optional[list] = None, search_filter: Optional[ClearanceFilter] = None
    ) -> int:
        """Get the number of Clearance objects matching the search terms"""
        search_filter = search_filter or self.search_filter
        return self.search(
            search_filter=search_filter,
            terms=terms,
            search_options={"CountOnly": True},
        )

    def update(self, *args, **kwargs) -> ACSRequestResponse:
        raise ACSNotImplementedException("Updating clearances is not currently supported.")

    def create(self, *args, **kwargs) -> ACSRequestResponse:
        raise ACSNotImplementedException("Creating clearances is not currently supported.")

    def delete(self, *args, **kwargs) -> ACSRequestResponse:
        raise ACSNotImplementedException("Deleting clearances is not currently supported.")


class CcureCredential(CcureACS):
    def __init__(self, connection: Optional[CcureConnection] = None):
        super().__init__(connection)
        self.search_filter = CredentialFilter()
        self.type = ObjectType.CREDENTIAL.complete

    def search(
        self,
        terms: Optional[list] = None,
        search_filter: Optional[CredentialFilter] = None,
        page_size: Optional[int] = None,
        page_number: int = 1,
        timeout: int = 0,
        search_options: Optional[dict] = None,
        where_clause: Optional[str] = None,
    ) -> list:
        """
        Get a list of Credential objects matching given search terms

        :param terms: list of search terms
        :param search filter: specifies how and in what fields to look for the search terms
        """
        self.logger.info("Searching for credentials")
        search_filter = search_filter or self.search_filter
        return super().search(
            object_type=self.type,
            search_filter=search_filter,
            terms=terms,
            page_size=page_size,
            page_number=page_number,
            timeout=timeout,
            search_options=search_options,
            where_clause=where_clause,
        )

    def get_property(self, object_id: int, property_name: str) -> Any:
        return super().get_property(self.type, object_id, property_name)

    def count(
        self, terms: Optional[list] = None, search_filter: Optional[CredentialFilter] = None
    ) -> int:
        """Get the number of Credential objects matching the search"""
        search_filter = search_filter or self.search_filter
        return self.search(
            search_filter=search_filter,
            terms=terms,
            search_options={"CountOnly": True},
        )

    def update(self, record_id: int, update_data: dict) -> ACSRequestResponse:
        """
        Edit properties of a Credential object

        :param record_id: the Credential object's CCure ID
        :param update_data: maps Credential properties to their new values
        """
        return super().update(object_type=self.type, object_id=record_id, update_data=update_data)

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
        return self.add_children(
            parent_type=ObjectType.PERSONNEL.complete,
            parent_id=personnel_id,
            child_type=ObjectType.CREDENTIAL.complete,
            child_configs=[create_data_dict],
        )

    def delete(self, record_id: int) -> ACSRequestResponse:
        """Delete a Credential object by its CCure ID"""
        return super().delete(object_type=self.type, object_id=record_id)


class CcureClearanceItem(CcureACS):
    """API interactions for doors and elevators"""

    def __init__(self, connection: Optional[CcureConnection] = None):
        super().__init__(connection)
        self.search_filter = ClearanceItemFilter()
        self.type = ObjectType.CLEARANCE_ITEM.complete

    def search(
        self,
        terms: Optional[list] = None,
        search_filter: Optional[ClearanceItemFilter] = None,
        page_size: Optional[int] = None,
        page_number: int = 1,
        timeout: float = 0,
        search_options: Optional[dict] = None,
        where_clause: Optional[str] = None,
    ) -> list:
        """
        Get a list of ClearanceItem objects matching given search terms

        :param terms: list of search terms
        :param search filter: specifies how and in what fields to look for the search terms
        """
        self.logger.info("Searching for clearance items")
        search_filter = search_filter or self.search_filter
        return super().search(
            object_type=self.type,
            search_filter=search_filter,
            terms=terms,
            page_size=page_size,
            page_number=page_number,
            timeout=timeout,
            search_options=search_options,
            where_clause=where_clause,
        )

    def get_property(self, object_type: str, object_id: int, property_name: str) -> Any:
        return super().get_property(object_type, object_id, property_name)

    def get_lock_state(self, door_id: int):
        mode_status = self.get_property(ObjectType.DOOR.complete, door_id, "ModeStatus")
        return {
            0: "Unknown",
            1: "Unlocked",
            2: "Locked",
            3: "No Access",
            4: "Momentary Unlock",
        }.get(mode_status, "Unknown")

    def count(
        self,
        terms: Optional[list] = None,
        search_filter: Optional[PersonnelFilter] = None,
    ) -> int:
        """Get the total number of ClearanceItem objects"""
        search_filter = search_filter or self.search_filter
        return self.search(
            search_filter=search_filter,
            terms=terms,
            search_options={"CountOnly": True},
        )

    def update(self, item_id: int, update_data: dict) -> ACSRequestResponse:
        """
        Edit properties of a ClearanceItem object

        :param item_id: the ClearanceItem object's CCure ID
        :param update_data: maps ClearanceItem properties to their new values
        """
        return super().update(object_type=self.type, object_id=item_id, update_data=update_data)

    def create(
        self,
        child_type: str,
        controller_id: int,
        create_data: ClearanceItemCreateData,
    ) -> ACSRequestResponse:
        """
        Create a new clearance item object

        :param child_type: eg ObjectType.DOOR, ObjectType.ELEVATOR
        :param controller_id: object ID for the iStarController object for the new clearance item
        :param create_data: object with properties required to create a new clearance item
        """
        create_data_dict = create_data.model_dump()

        return self.add_children(
            parent_type=ObjectType.ISTAR_CONTROLLER,
            parent_id=controller_id,
            child_type=child_type.complete,
            child_configs=[create_data_dict],
        )

    def delete(self, item_id: int) -> ACSRequestResponse:
        """Delete a ClearanceItem object by its CCure ID"""
        return super().delete(object_type=self.type, object_id=item_id)


class CcureGroup(CcureACS):
    def __init__(self, connection: Optional[CcureConnection] = None):
        super().__init__(connection)
        self.search_filter = GroupFilter()
        self.type = ObjectType.GROUP.complete

    def search(
        self,
        terms: Optional[list] = None,
        search_filter: Optional[GroupFilter] = None,
        page_size: Optional[int] = None,
        page_number: int = 1,
        timeout: float = 0,
        search_options: Optional[dict] = None,
        where_clause: Optional[str] = None,
    ) -> list:
        self.logger.info("Searching for Clearance Item Group")
        search_filter = search_filter or self.search_filter
        return super().search(
            object_type=self.type,
            search_filter=search_filter,
            terms=terms,
            page_size=page_size,
            page_number=page_number,
            timeout=timeout,
            search_options=search_options,
            where_clause=where_clause,
        )

    def get_property(self, object_id: int, property_name: str) -> Any:
        return super().get_property(self.type, object_id, property_name)

    def count(
        self,
        terms: Optional[list] = None,
        search_filter: Optional[GroupFilter] = None,
    ) -> int:
        """Get the total number of Clearance Group objects"""
        search_filter = search_filter or self.search_filter
        return self.search(
            search_filter=search_filter,
            terms=terms,
            search_options={"CountOnly": True},
        )

    def update(self, *args, **kwargs) -> ACSRequestResponse:
        raise ACSNotImplementedException("Updating groups is not currently supported.")

    def create(self, *args, **kwargs) -> ACSRequestResponse:
        raise ACSNotImplementedException("Creating groups is not currently supported.")

    def delete(self, *args, **kwargs) -> ACSRequestResponse:
        raise ACSNotImplementedException("Deleting groups is not currently supported.")


class CcureGroupMember(CcureACS):
    def __init__(self, connection: Optional[CcureConnection] = None):
        super().__init__(connection)
        self.search_filter = GroupMemberFilter()
        self.type = ObjectType.GROUP_MEMBER.complete

    def search(
        self,
        terms: Optional[list] = None,
        search_filter: Optional[GroupMemberFilter] = None,
        page_size: Optional[int] = None,
        page_number: int = 1,
        timeout: float = 0,
        search_options: Optional[dict] = None,
        where_clause: Optional[str] = None,
    ) -> list:
        self.logger.info("Searching for Clearance Item Group members")
        search_filter = search_filter or self.search_filter
        return super().search(
            object_type=self.type,
            search_filter=search_filter,
            terms=terms,
            page_size=page_size,
            page_number=page_number,
            timeout=timeout,
            search_options=search_options,
            where_clause=where_clause,
        )

    def get_property(self, object_id: int, property_name: str) -> Any:
        return super().get_property(self.type, object_id, property_name)

    def count(
        self,
        terms: Optional[list] = None,
        search_filter: Optional[GroupMemberFilter] = None,
    ) -> int:
        """Get the total number of Clearance Group objects"""
        search_filter = search_filter or self.search_filter
        return self.search(
            search_filter=search_filter,
            terms=terms,
            search_options={"CountOnly": True},
        )

    def update(self, *args, **kwargs) -> ACSRequestResponse:
        raise ACSNotImplementedException("Updating groups is not currently supported.")

    def create(self, *args, **kwargs) -> ACSRequestResponse:
        raise ACSNotImplementedException("Creating groups is not currently supported.")

    def delete(self, *args, **kwargs) -> ACSRequestResponse:
        raise ACSNotImplementedException("Deleting groups is not currently supported.")


class CcureJournal(CcureACS):
    def __init__(self, connection: CcureConnection):
        super().__init__(connection)
        self.search_filter = JournalFilter()
        self.type = ObjectType.JOURNAL.complete  # TODO maybe not?

    def search(
        self,
        start_time: datetime,
        end_time: datetime,
        object_type: str,
        object_guid: str,
        message_types: list[str] = ["CardAdmitted", "CardRejected"],
        page_size: Optional[int] = None,
        page_number: int = 1,
        timeout: float = 0,
        sort_by: str = "ServerUTC DESC",
        partition: int = 1,
    ) -> list:
        """
        Get a list of transaction journal entries matching the given person and/or door
        Can only filter by one guid per api call

        :param terms: list of search terms
        :param search filter: specifies how and in what fields to look for the search terms
        """
        try:
            UUID(object_guid)
        except ValueError:
            raise ACSRequestException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                f"Search filter must be a valid GUID, got '{object_guid}'",
            )

        TIME_FORMAT = "%m/%d/%Y %-I:%M:%S %p"  # MM/DD/YYYY h:mm:ss XM
        if page_size is None:
            page_size = super().config.page_size
        request_json = {
            "startDateTime": start_time.strftime(TIME_FORMAT),
            "endDateTime": end_time.strftime(TIME_FORMAT),
            "objectType": object_type,
            "objectGuid": object_guid,
            "sortOrder": sort_by,
            "pageSize": page_size,
            "pageNumber": page_number,
            "messageTypes": message_types,
            "partitionId": partition,
        }
        response = self.connection.request(
            ACSRequestMethod.POST,
            request_data=ACSRequestData(
                url=self.connection.config.base_url + self.connection.config.endpoints.JOURNALS,
                request_json=request_json,
                headers=self.connection.base_headers,
            ),
            timeout=timeout,
        )
        return response.json[1:]  # the first item is just metadata

    def count(
        self,
        terms: Optional[list] = None,
        search_filter: Optional[JournalFilter] = None,
        where_clause: Optional[str] = None,
    ) -> int:
        """Get the total number of Journal objects"""
        search_filter = search_filter or self.search_filter
        return super().search(
            object_type=self.type,
            search_filter=search_filter,
            where_clause=where_clause,
            terms=terms,
            search_options={"CountOnly": True},
        )

    def get_property(self, *args, **kwargs):
        raise ACSNotImplementedException("CcureJournal.get_property is not currently supported.")

    def update(self, *args, **kwargs):
        raise ACSNotImplementedException("Updating journals is not currently supported.")

    def create(self, *args, **kwargs):
        raise ACSNotImplementedException("Creating groups is not currently supported.")

    def delete(self, *args, **kwargs):
        raise ACSNotImplementedException("Deleting journals is not currently supported.")
