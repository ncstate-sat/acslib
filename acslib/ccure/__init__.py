from typing import Optional

from acslib.base import ACSRequestResponse
from acslib.base.connection import ACSRequestData, ACSRequestMethod
from acslib.ccure.base import CcureACS
from acslib.ccure.connection import CcureConnection
from acslib.ccure.crud import (
    CcurePersonnel,
    CcureClearance,
    CcureCredential,
    CcureClearanceItem,
)
from acslib.ccure.filters import ClearanceFilter, PersonnelFilter, CredentialFilter


class CcureAPI:
    def __init__(self, connection: Optional[CcureConnection] = None):
        self.personnel = CcurePersonnel(connection)
        self.clearance = CcureClearance(connection)
        self.credential = CcureCredential(connection)
        self.clearance_item = CcureClearanceItem(connection)
        self.object = CcureACS(connection)  # TODO rename
