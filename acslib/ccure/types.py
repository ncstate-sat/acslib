from enum import Enum


class ClearanceItemType(Enum):
    DOOR = "door"
    ELEVATOR = "elevator"

    @property
    def complete(self):
        if self == self.DOOR:
            return "SoftwareHouse.NextGen.Common.SecurityObjects.Door"
        if self == self.ELEVATOR:
            return "SoftwareHouse.NextGen.Common.SecurityObjects.Elevator"
