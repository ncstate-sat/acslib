from typing import Optional

from acslib.base import ACSRequestResponse
from acslib.base.connection import ACSRequestData, ACSRequestMethod
from acslib.ccure.actions import CcureAction
from acslib.ccure.base import CcureACS
from acslib.ccure.connection import CcureConnection
from acslib.ccure.crud import (
    CcurePersonnel,
    CcureClearance,
    CcureCredential,
    CcureClearanceItem,
    CcureGroup,
    CcureGroupMember,
)
from acslib.ccure.filters import (
    ClearanceFilter,
    PersonnelFilter,
    CredentialFilter,
    GroupFilter,
    GroupMemberFilter,
)


class CcureAPI:
    def __init__(self, connection: Optional[CcureConnection] = None):
        self.connection = connection or CcureConnection()
        self.personnel = CcurePersonnel(self.connection)
        self.clearance = CcureClearance(self.connection)
        self.credential = CcureCredential(self.connection)
        self.clearance_item = CcureClearanceItem(self.connection)
        self.action = CcureAction(self.connection)
        self.ccure_object = CcureACS(self.connection)
        self.group = CcureGroup(self.connection)
        self.group_member = CcureGroupMember(self.connection)
