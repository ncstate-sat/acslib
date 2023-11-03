from dataclasses import dataclass


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
