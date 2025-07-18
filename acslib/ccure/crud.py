from numbers import Number
from typing import Any, Optional

from acslib.base import ACSRequestResponse
from acslib.base.connection import ACSNotImplementedException
from acslib.ccure.base import CcureACS
from acslib.ccure.connection import CcureConnection
from acslib.ccure.filters import (
    ClearanceFilter,
    ClearanceItemFilter,
    CredentialFilter,
    PersonnelFilter,
    GroupFilter,
    GroupMemberFilter,
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
        page_size: Optional[int] = None,
        page_number: int = 1,
        timeout: Number = 0,
        search_options: Optional[dict] = None,
        where_clause: Optional[str] = None,
    ) -> list:
        """
        Get a list of Personnel objects matching given search terms

        :param terms: list of search terms
        :param search filter: specifies how and in what fields to look for the search terms
        """
        self.logger.info("Searching for personnel")
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
        timeout: Number = 0,
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

    def search(
        self,
        item_type: str,
        terms: Optional[list] = None,
        search_filter: Optional[ClearanceItemFilter] = None,
        page_size: Optional[int] = None,
        page_number: int = 1,
        timeout: Number = 0,
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
            object_type=item_type,
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
        item_type: str,
        terms: Optional[list] = None,
        search_filter: Optional[PersonnelFilter] = None,
    ) -> int:
        """Get the total number of ClearanceItem objects"""
        search_filter = search_filter or self.search_filter
        return self.search(
            item_type=item_type,
            search_filter=search_filter,
            terms=terms,
            search_options={"CountOnly": True},
        )

    def update(self, item_type: str, item_id: int, update_data: dict) -> ACSRequestResponse:
        """
        Edit properties of a ClearanceItem object

        :param item_type: specifies an item type. eg ObjectType.DOOR
        :param item_id: the ClearanceItem object's CCure ID
        :param update_data: maps ClearanceItem properties to their new values
        """
        return super().update(object_type=item_type, object_id=item_id, update_data=update_data)

    def create(
        self,
        item_type: str,
        controller_id: int,
        create_data: ClearanceItemCreateData,
    ) -> ACSRequestResponse:
        """
        Create a new clearance item object

        :param item_type: eg ObjectType.DOOR, ObjectType.ELEVATOR
        :param controller_id: object ID for the iStarController object for the new clearance item
        :param create_data: object with properties required to create a new clearance item
        """
        create_data_dict = create_data.model_dump()

        return self.add_children(
            parent_type=ObjectType.ISTAR_CONTROLLER,
            parent_id=controller_id,
            child_type=item_type.complete,
            child_configs=[create_data_dict],
        )

    def delete(self, item_type: str, item_id: int) -> ACSRequestResponse:
        """Delete a ClearanceItem object by its CCure ID"""
        return super().delete(object_type=item_type, object_id=item_id)


class CcureGroup(CcureACS):
    def __init__(self, connection: Optional[CcureConnection] = None):
        super().__init__(connection)
        self.search_filter = GroupFilter()

    def search(
        self,
        item_type: str,
        terms: Optional[list] = None,
        search_filter: Optional[GroupFilter] = None,
        page_size: Optional[int] = None,
        page_number: int = 1,
        timeout: Number = 0,
        search_options: Optional[dict] = None,
        where_clause: Optional[str] = None,
    ) -> list:
        self.logger.info("Searching for Clearance Item Group")
        search_filter = search_filter or self.search_filter
        return super().search(
            object_type=item_type,
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
        item_type: str,
        terms: Optional[list] = None,
        search_filter: Optional[GroupFilter] = None,
    ) -> int:
        """Get the total number of Clearance Group objects"""
        search_filter = search_filter or self.search_filter
        return self.search(
            item_type=item_type,
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

    def search(
        self,
        item_type: str,
        terms: Optional[list] = None,
        search_filter: Optional[GroupMemberFilter] = None,
        page_size: Optional[int] = None,
        page_number: int = 1,
        timeout: Number = 0,
        search_options: Optional[dict] = None,
        where_clause: Optional[str] = None,
    ) -> list:
        self.logger.info("Searching for Clearance Item Group")
        search_filter = search_filter or self.search_filter
        return super().search(
            object_type=item_type,
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
        item_type: str,
        terms: Optional[list] = None,
        search_filter: Optional[GroupMemberFilter] = None,
    ) -> int:
        """Get the total number of Clearance Group objects"""
        search_filter = search_filter or self.search_filter
        return self.search(
            item_type=item_type,
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
