from enum import Enum


class ObjectType(Enum):
    CLEARANCE = "clearance"
    CLEARANCE_ASSIGNMENT = "clearance assignment"
    CREDENTIAL = "credential"
    CLEARANCE_ITEM = "clearance item"
    DOOR = "door"
    ELEVATOR = "elevator"
    IMAGE = "image"
    ISTAR_CONTROLLER = "istar controller"
    PERSONNEL = "personnel"
    TIME_SPEC = "time spec"

    @property
    def complete(self):
        if self == self.CLEARANCE:
            return "SoftwareHouse.NextGen.Common.SecurityObjects.Clearance"
        if self == self.CLEARANCE_ASSIGNMENT:
            return "SoftwareHouse.NextGen.Common.SecurityObjects.PersonnelClearancePair"
        if self == self.CREDENTIAL:
            return "SoftwareHouse.NextGen.Common.SecurityObjects.Credential"
        if self == self.CLEARANCE_ITEM:
            return "SoftwareHouse.NextGen.Common.SecurityObjects.ClearanceItem"
        if self == self.DOOR:
            return "SoftwareHouse.NextGen.Common.SecurityObjects.Door"
        if self == self.ELEVATOR:
            return "SoftwareHouse.NextGen.Common.SecurityObjects.Elevator"
        if self == self.IMAGE:
            return "SoftwareHouse.NextGen.Common.SecurityObjects.Images"
        if self == self.ISTAR_CONTROLLER:
            return "SoftwareHouse.NextGen.Common.SecurityObjects.iStarController"
        if self == self.PERSONNEL:
            return "SoftwareHouse.NextGen.Common.SecurityObjects.Personnel"
        if self == self.TIME_SPEC:
            return "SoftwareHouse.CrossFire.Common.Objects.TimeSpec"


class ImageType(Enum):
    UNKNOWN = 0
    PORTRAIT = 1
    SIGNATURE = 2
    FINGERPRINT = 3
    HANDPRINT = 4
    DYNAMIC_BADGE_IMAGE = 5
    STATIC_BADGE_IMAGE = 6
    SYSTEM_IMAGE = 7
    PRIVATE_IMAGE = 8
    SHARED_IMAGE = 9
