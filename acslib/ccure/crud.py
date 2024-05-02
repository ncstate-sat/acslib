from datetime import datetime, timezone
from typing import Optional

from acslib.base import ACSRequestData, ACSRequestResponse, status, ACSRequestException
from acslib.base.connection import ACSRequestMethod
from acslib.ccure.base import CcureACS
from acslib.ccure.connection import CcureConnection
from acslib.ccure.filters import (
    ClearanceFilter,
    ClearanceItemFilter,
    CredentialFilter,
    PersonnelFilter,
    CcureFilter,
    NFUZZ,
)
from acslib.ccure.data_models import (
    ClearanceItemCreateData,
    CredentialCreateData,
    PersonnelCreateData,
)
from acslib.ccure.types import ObjectType, ImageType


class CcurePersonnel(CcureACS):
    def __init__(self, connection: Optional[CcureConnection] = None):
        super().__init__(connection)
        self.search_filter = PersonnelFilter()
        self.type = ObjectType.PERSONNEL.complete

    def search(
        self,
        terms: list,
        search_filter: Optional[PersonnelFilter] = None,
        page_size=100,  # TODO parameterize
        page_number=1,
        params: dict = {},
    ) -> list:
        """
        Get a list of Personnel objects matching given search terms

        :param terms: list of search terms
        :param search filter: specifies how and in what fields to look for the search terms
        """
        self.logger.info("Searching for personnel")
        search_filter = search_filter or self.search_filter

        return super().search(  # TODO rename base methods and call self instead of super?
            object_type=self.type,
            terms=terms,
            search_filter=search_filter,
            page_size=page_size,
            page_number=page_number,
            params=params,
        )

    def count(
        self, terms: Optional[list] = [], search_filter: Optional[PersonnelFilter] = None
    ) -> int:
        """Get the total number of Personnel objects"""
        search_filter = search_filter or self.search_filter
        return self.search(
            terms=terms,
            search_filter=search_filter,
            params={"CountOnly": True},
        )

    def update(self, personnel_id: int, update_data: dict) -> ACSRequestResponse:
        """
        Edit properties of a personnel object

        :param personnel_id: the Personnel object's CCure ID
        :param update_data: maps Personnel properties to their new values
        """
        return super().update(
            object_type=self.type, object_id=personnel_id, update_data=update_data
        )

    def create(self, create_data: PersonnelCreateData) -> ACSRequestResponse:
        """
        Create a new personnel object

        create_data must contain a 'LastName' property.
        """
        create_data_dict = create_data.model_dump()
        request_data = create_data_dict | {"ClassType": self.type}
        return super().create(request_data=request_data)

    def delete(self, personnel_id: int) -> ACSRequestResponse:
        """Delete a personnel object by its CCure ID"""
        return super().delete(object_type=self.type, object_id=personnel_id)

    def add_image(
        self, personnel_id: int, image: str, image_name: str = "", partition_id: int = 1
    ) -> ACSRequestResponse:
        """
        Set an image to a personnel object's PrimaryPortrait property
        - `image` is base-64 encoded.
        - `image_name` must be unique.
        - `partition_id` refers to the partition where the personnel object is stored.
        """
        if not image_name:
            timestamp = int(datetime.now(timezone.utc).timestamp())
            image_name = f"{personnel_id}_{timestamp}"
        image_properties = {
            "Name": image_name,
            "ParentId": personnel_id,
            "ImageType": ImageType.PORTRAIT.value,
            "PartitionID": partition_id,
            "Primary": True,  # we're only adding primary portraits
            "Image": image,
        }
        return self.add_children(
            parent_type=ObjectType.PERSONNEL.complete,
            parent_id=personnel_id,
            child_type=ObjectType.IMAGE.complete,
            child_configs=[image_properties],
        )

    def get_image(self, personnel_id: int) -> Optional[str]:  # TODO do we even need this?
        """
        Get the `PrimaryPortrait` property for the person with the given personnel ID.
        The returned image is a base-64 encoded string.
        """
        return self.get_property(self.type, personnel_id, "PrimaryPortrait")

    def assign_clearances(self, personnel_id: int, clearance_ids: list[int]) -> ACSRequestResponse:
        """Assign clearances to a person"""
        clearance_assignment_properties = [
            {"PersonnelID": personnel_id, "ClearanceID": clearance_id}
            for clearance_id in clearance_ids
        ]
        return self.add_children(
            parent_type=ObjectType.PERSONNEL.complete,
            parent_id=personnel_id,
            child_type=ObjectType.CLEARANCE_ASSIGNMENT.complete,
            child_configs=clearance_assignment_properties,
        )

    def revoke_clearances(self, personnel_id: int, clearance_ids: list[int]) -> ACSRequestResponse:
        """
        Revoke a person's clearances
        Two steps: 1: Get the PersonnelClearancePair object IDs
                   2: Remove those PersonnelClearancePair objects
        """  # TODO should we even do this? should acslib do two-step functions?

        # get PersonnelClearancePair object IDs
        clearance_query = " OR ".join(
            f"ClearanceID = {clearance_id}" for clearance_id in clearance_ids
        )
        assignment_ids = super().search(
            object_type=ObjectType.CLEARANCE_ASSIGNMENT.complete,
            terms=[personnel_id],
            page_size=0,
            where_clause=f"PersonnelID = {personnel_id} AND ({clearance_query})",
        )

        # remove PersonnelClearancePair objects
        return self.remove_children(
            parent_type=self.type,
            parent_id=personnel_id,
            child_type=ObjectType.CLEARANCE_ASSIGNMENT.complete,
            child_ids=assignment_ids,
        )

    def get_assigned_clearances(
        self, personnel_id: int, page_size=100, page_number=1
    ) -> list[dict]:
        """Get the clearance assignments associated with a person"""
        search_filter = CcureFilter(
            lookups={"PersonnelID": NFUZZ}, display_properties=["PersonnelID", "ClearanceID"]
        )
        return super().search(
            object_type=ObjectType.CLEARANCE_ASSIGNMENT.complete,
            terms=[personnel_id],
            search_filter=search_filter,
            page_size=page_size,
            page_number=page_number,
        )


class CcureClearance(CcureACS):
    def __init__(self, connection: Optional[CcureConnection] = None):
        super().__init__(connection)
        self.search_filter = ClearanceFilter()
        self.type = ObjectType.CLEARANCE.complete

    def search(
        self,
        terms: list,
        search_filter: Optional[ClearanceFilter] = None,
        page_size=100,  # TODO parameterize
        page_number=1,
        params: dict = {},
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
            terms=terms,
            search_filter=search_filter,
            page_size=page_size,
            page_number=page_number,
            params=params,  # TODO rename params
        )

    def count(
        self, terms: Optional[list] = [], search_filter: Optional[ClearanceFilter] = None
    ) -> int:
        """Get the number of Clearance objects matching the search terms"""
        search_filter = search_filter or self.search_filter
        return self.search(
            terms=terms,
            search_filter=search_filter,
            params={"CountOnly": True},
        )

    def get_assignees(self, clearance_id: int, page_size=100, page_number=1) -> list[dict]:
        search_filter = CcureFilter(
            lookups={"ClearanceID": NFUZZ}, display_properties=["PersonnelID", "ClearanceID"]
        )
        return super().search(
            object_type=ObjectType.CLEARANCE_ASSIGNMENT.complete,
            terms=[clearance_id],
            search_filter=search_filter,
            page_size=page_size,
            page_number=page_number,
        )

    def update(self, *args, **kwargs) -> ACSRequestResponse:
        raise ACSRequestException(  # TODO use a new exception type instead of the base?
            status.HTTP_501_NOT_IMPLEMENTED, "Updating clearances is not currently supported."
        )

    def create(self, *args, **kwargs) -> ACSRequestResponse:
        raise ACSRequestException(
            status.HTTP_501_NOT_IMPLEMENTED, "Creating clearances is not currently supported."
        )

    def delete(self, *args, **kwargs) -> ACSRequestResponse:
        raise ACSRequestException(
            status.HTTP_501_NOT_IMPLEMENTED, "Deleting clearances is not currently supported."
        )


class CcureCredential(CcureACS):
    def __init__(self, connection: Optional[CcureConnection] = None):
        super().__init__(connection)
        self.search_filter = CredentialFilter()
        self.type = ObjectType.CREDENTIAL.complete

    def search(
        self,
        terms: Optional[list] = None,
        search_filter: Optional[CredentialFilter] = None,
        page_size=100,  # TODO parameterize
        page_number=1,
        params: dict = {},
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
            terms=terms,
            search_filter=search_filter,
            page_size=page_size,
            page_number=page_number,
            params=params,
        )

    def count(
        self, terms: Optional[list] = [], search_filter: Optional[CredentialFilter] = None
    ) -> int:
        """Get the number of Credential objects matching the search"""
        search_filter = search_filter or self.search_filter
        return self.search(
            terms=terms,
            search_filter=search_filter,
            params={"CountOnly": True},
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
        item_type: ObjectType,
        terms: Optional[list] = None,
        search_filter: Optional[ClearanceItemFilter] = None,
        page_size=100,  # TODO parameterize
        page_number=1,
        params: dict = {},
    ) -> list:
        """
        Get a list of ClearanceItem objects matching given search terms

        :param terms: list of search terms
        :param search filter: specifies how and in what fields to look for the search terms
        """
        self.logger.info("Searching for clearance items")
        search_filter = search_filter or self.search_filter
        return super().search(  # TODO rename base methods and call self instead of super?
            object_type=item_type.complete,
            terms=terms,
            search_filter=search_filter,
            page_size=page_size,
            page_number=page_number,
            params=params,
        )

    def count(
        self,
        item_type: ObjectType,
        terms: Optional[list] = [],
        search_filter: Optional[PersonnelFilter] = None,
    ) -> int:
        """Get the total number of ClearanceItem objects"""
        search_filter = search_filter or self.search_filter
        return self.search(
            item_type=item_type.complete,
            terms=terms,
            search_filter=search_filter,
            params={"CountOnly": True},
        )

    def update(self, item_type: ObjectType, item_id: int, update_data: dict) -> ACSRequestResponse:
        """
        Edit properties of a ClearanceItem object

        :param item_type: specifies an item type. eg ClearanceItemType.DOOR
        :param item_id: the ClearanceItem object's CCure ID
        :param update_data: maps ClearanceItem properties to their new values
        """
        return super().update(
            object_type=item_type.complete, object_id=item_id, update_data=update_data
        )

    def create(
        self,
        item_type: ObjectType,
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

        return self.add_children(
            parent_type=ObjectType.ISTAR_CONTROLLER.complete,
            parent_id=controller_id,
            child_type=item_type.complete,
            child_configs=[create_data_dict],
        )

    def delete(self, item_type: ObjectType, item_id: int) -> ACSRequestResponse:
        """Delete a ClearanceItem object by its CCure ID"""
        return super().delete(object_type=item_type.complete, object_id=item_id)
