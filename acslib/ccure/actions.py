"""Use CCure CRUD operations to perform some common actions"""

from datetime import datetime, timezone
from typing import Optional

from acslib.base import (
    ACSRequestData,
    ACSRequestResponse,
    ACSRequestException,
    status,
)
from acslib.ccure.base import CcureACS
from acslib.ccure.connection import CcureConnection, ACSRequestMethod
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


class DoorAction(CcureACS):
    def __init__(self, connection: Optional[CcureConnection] = None):
        super().__init__(connection)
        self.type = ObjectType.DOOR.complete

    def lock(
        self,
        door_id: int,
        lock_time: Optional[datetime] = None,
        unlock_time: Optional[datetime] = None,
        priority: Optional[int] = None,
        source_name: str = "acslib",
    ):
        """
        Lock a door for a set period of time
        `lock_time`, `unlock_time`, and `priority` are optional.
        If there are multiple conflicting schedules, the schedule with the higher priority value
            will take precedence
        `source_name` refers to the client application making the request
        """
        if lock_time and unlock_time and lock_time > unlock_time:
            raise ACSRequestException(
                status_code=status.HTTP_400_BAD_REQUEST,
                log_message="unlock_time must be after lock_time.",
            )
        TIME_FORMAT = "%m/%d/%Y %H:%M:%S"  # MM/DD/YYYY hh:mm:ss
        property_names = ["TargetType", "TargetID"]
        property_values = [ObjectType.ISTAR_DOOR.complete, door_id]
        if lock_time:
            property_names.append("StartTime")
            property_values.append(lock_time.strftime(TIME_FORMAT))
        if unlock_time:
            property_names.append("EndTime")
            property_values.append(unlock_time.strftime(TIME_FORMAT))
        if priority:
            property_names.append("Priority")
            property_values.append(priority)
        request_data = {
            "PropertyNames": property_names,
            "PropertyValues": property_values,
            "sourceName": source_name,
        }
        return self.connection.request(
            ACSRequestMethod.POST,
            request_data=ACSRequestData(
                url=self.config.base_url + self.config.endpoints.ACTION,
                params={"actionTypeFullName": "SoftwareHouse.NextGen.Common.Actions.LockDoor"},
                data=self.connection.encode_data(request_data),
                headers=self.connection.base_headers | self.connection.header_for_form_data,
            ),
        )

    def unlock(
        self,
        door_id: int,
        unlock_time: Optional[datetime] = None,
        lock_time: Optional[datetime] = None,
        priority: Optional[int] = None,
        source_name: str = "acslib",
    ):
        """
        Unlock a door for a set period of time
        `unlock_time`, `lock_time`, and `priority` are optional.
        If there are multiple conflicting schedules, the schedule with the higher priority value
            will take precedence
        `source_name` refers to the client application making the request
        """
        if unlock_time and lock_time and unlock_time > lock_time:
            raise ACSRequestException(
                status_code=status.HTTP_400_BAD_REQUEST,
                log_message="lock_time must be after unlock_time.",
            )
        TIME_FORMAT = "%m/%d/%Y %H:%M:%S"  # MM/DD/YYYY hh:mm:ss
        property_names = ["TargetType", "TargetID"]
        property_values = [ObjectType.ISTAR_DOOR.complete, door_id]
        if unlock_time:
            property_names.append("StartTime")
            property_values.append(unlock_time.strftime(TIME_FORMAT))
        if lock_time:
            property_names.append("EndTime")
            property_values.append(lock_time.strftime(TIME_FORMAT))
        if priority:
            property_names.append("Priority")
            property_values.append(priority)

        request_data = {
            "PropertyNames": property_names,
            "PropertyValues": property_values,
            "sourceName": source_name,
        }
        return self.connection.request(
            ACSRequestMethod.POST,
            request_data=ACSRequestData(
                url=self.config.base_url + self.config.endpoints.ACTION,
                params={"actionTypeFullName": "SoftwareHouse.NextGen.Common.Actions.UnLockDoor"},
                data=self.connection.encode_data(request_data),
                headers=self.connection.base_headers | self.connection.header_for_form_data,
            ),
        )


class CcureAction:
    def __init__(self, connection: Optional[CcureConnection] = None):
        self.personnel = PersonnelAction(connection)
        self.clearance = ClearanceAction(connection)
        self.door = DoorAction(connection)
