"""Use CCure CRUD operations to perform some common actions"""

from datetime import datetime, timezone
from typing import Optional

from acslib.base import ACSRequestResponse
from acslib.ccure.base import CcureACS
from acslib.ccure.connection import CcureConnection
from acslib.ccure.filters import (
    CcureFilter,
    ClearanceFilter,
    PersonnelFilter,
    NFUZZ,
)
from acslib.ccure.types import ObjectType, ImageType


class PersonnelAction(CcureACS):
    def __init__(self, connection: Optional[CcureConnection] = None):
        super().__init__(connection)
        self.search_filter = PersonnelFilter()
        self.type = ObjectType.PERSONNEL.complete

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
        Two steps:
            1: Get the PersonnelClearancePair object IDs
            2: Remove those PersonnelClearancePair objects
        """

        # get PersonnelClearancePair object IDs
        clearance_query = " OR ".join(
            f"ClearanceID = {clearance_id}" for clearance_id in clearance_ids
        )
        search_filter = CcureFilter(display_properties=["PersonnelID", "ObjectID"])
        clearance_assignments = super().search(
            object_type=ObjectType.CLEARANCE_ASSIGNMENT.complete,
            search_filter=search_filter,
            terms=[personnel_id],
            page_size=0,
            where_clause=f"PersonnelID = {personnel_id} AND ({clearance_query})",
        )
        assignment_ids = [assignment.get("ObjectID") for assignment in clearance_assignments]

        if assignment_ids:
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
        """Get personnel/clearance pairs associated with the given person"""
        search_filter = CcureFilter(
            lookups={"PersonnelID": NFUZZ}, display_properties=["PersonnelID", "ClearanceID"]
        )
        return super().search(
            object_type=ObjectType.CLEARANCE_ASSIGNMENT.complete,
            search_filter=search_filter,
            terms=[personnel_id],
            page_size=page_size,
            page_number=page_number,
        )

    def add_image(
        self, personnel_id: int, image: str, image_name: str = "", partition_id: int = 1
    ) -> ACSRequestResponse:
        """
        Set an image to a personnel object's PrimaryPortrait property
        - `image` is base-64 url-encoded.
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
            "Primary": True,  # this only adds primary portraits
            "Image": image,
        }
        return self.add_children(
            parent_type=ObjectType.PERSONNEL.complete,
            parent_id=personnel_id,
            child_type=ObjectType.IMAGE.complete,
            child_configs=[image_properties],
        )

    def get_image(self, personnel_id: int) -> Optional[str]:
        """
        Get the `PrimaryPortrait` property for the person with the given personnel ID.
        The returned image is a base-64 encoded string.
        """
        return self.get_property(self.type, personnel_id, "PrimaryPortrait")


class ClearanceAction(CcureACS):
    def __init__(self, connection: Optional[CcureConnection] = None):
        super().__init__(connection)
        self.search_filter = ClearanceFilter()
        self.type = ObjectType.CLEARANCE.complete

    def get_assignees(self, clearance_id: int, page_size=100, page_number=1) -> list[dict]:
        """Get clearance/personnel pairs belonging to the given clearance"""
        search_filter = CcureFilter(
            lookups={"ClearanceID": NFUZZ}, display_properties=["PersonnelID", "ClearanceID"]
        )
        return super().search(
            object_type=ObjectType.CLEARANCE_ASSIGNMENT.complete,
            search_filter=search_filter,
            terms=[clearance_id],
            page_size=page_size,
            page_number=page_number,
        )


class CcureAction:
    def __init__(self, connection: Optional[CcureConnection] = None):
        self.personnel = PersonnelAction(connection)
        self.clearance = ClearanceAction(connection)
