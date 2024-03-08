from typing import Optional

from pydantic import BaseModel, ConfigDict


class CredentialCreateData(BaseModel):
    CHUID: str
    CardNumber: Optional[int]
    FacilityCode: Optional[int]
    Name: Optional[str]

    model_config = ConfigDict(extra="allow")
