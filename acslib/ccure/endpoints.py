from dataclasses import dataclass

# from acslib.ccure.base import CcureACS
# from acslib.base.connection import ACSRequestData


@dataclass
class V2Endpoints:
    FIND_OBJS_W_CRITERIA = "/victorwebservice/api/Objects/FindObjsWithCriteriaFilter"
    CLEARANCES_FOR_ASSIGNMENT = "/victorwebservice/api/v2/Personnel/ClearancesForAssignment"
    GET_ALL_WITH_CRITERIA = "/victorwebservice/api/Objects/GetAllWithCriteria"
    PERSIST_TO_CONTAINER = "/victorwebservice/api/Objects/PersistToContainer"
    REMOVE_FROM_CONTAINER = "/victorwebservice/api/Objects/RemoveFromContainer"
    LOGIN = "/victorwebservice/api/Authenticate/Login"
    LOGOUT = "/victorwebservice/api/Authenticate/Logout"
    KEEPALIVE = "/victorwebservice/api/v2/session/keepalive"
    VERSIONS = "/victorwebservice/api/Generic/Versions"
    DISABLE = "/victorwebservice/api/v2/objects/SetProperty"
    SEARCH_CREDENTIALS = "/victorWebService/api/Objects/GetCredential"
    GET_CREDENTIALS = "/victorwebservice/api/v2/Credentials"
    DELETE_CREDENTIAL = "/victorwebservice/api/v2/Credentials/{_id}"


# class FindObjsWithCriteria(CcureACS):
#     def __init__(self, connection, **kwargs):
#         super().__init__(connection)
#         self.type_full_name = kwargs.get("type_full_name")
#         self.page_size = kwargs.get("page_size", self.connection.config.page_size)
#         self.page_number = kwargs.get("page_number", 1)
#         self.where_clause = kwargs.get("where_clause", "")
