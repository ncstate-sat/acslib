from typing import Optional

from pydantic import BaseModel, ConfigDict


class PersonnelCreateData(BaseModel):
    """
    Validates fields for creating new Personnel objects in CCure.

    Only the LastName field is required. All other Personnel model fields are also allowed.
    """

    LastName: str

    model_config = ConfigDict(extra="allow")


class CredentialCreateData(BaseModel):
    """
    Validates fields used for creating new Credential objects in CCure,
    corresponding to fields in the ACVSCore.Credential database table.

    CHUID is required to create a new Credential. Some other common fields are suggested,
    but any Credential property is allowed.
    """

    CHUID: str
    CardNumber: Optional[int] = None
    FacilityCode: Optional[int] = None
    Name: Optional[str] = None

    model_config = ConfigDict(extra="allow")


class ClearanceItemCreateData(BaseModel):
    Name: str
    Description: str
    ParentID: int
    ParentType: str
    ControllerID: int
    ControllerClassType: str

    model_config = ConfigDict(extra="allow")
