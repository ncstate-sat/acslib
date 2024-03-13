from typing import Optional

from pydantic import BaseModel, ConfigDict


class CredentialCreateData(BaseModel):
    CHUID: str
    CardNumber: Optional[int] = None
    FacilityCode: Optional[int] = None
    Name: Optional[str] = None

    model_config = ConfigDict(extra="allow")
