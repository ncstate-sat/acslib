from enum import Enum
from typing import Optional

from acslib.base.search import ACSFilter, BooleanOperators, TermOperators


def left_fuzz(term):
    return f"%{term}"


def right_fuzz(term):
    return f"{term}%"


def full_fuzz(term):
    return f"%{term}%"


def no_fuzz(term):
    return f"{term}"


LFUZZ = left_fuzz
RFUZZ = right_fuzz
FUZZ = full_fuzz
NFUZZ = no_fuzz

PERSONNEL_LOOKUP_FIELDS = {"FirstName": FUZZ, "LastName": FUZZ}
CLEARANCE_LOOKUP_FIELDS = {"Name": FUZZ}
CREDENTIAL_LOOKUP_FIELDS = {"Name": FUZZ}


class SearchTypes(Enum):
    PERSONNEL = "personnel"
    CLEARANCE = "clearance"
    CREDENTIAL = "credential"


class BaseCcureFilter(ACSFilter):
    """Base CCure Filter
    :param lookups: Dict containing searchable field names and their lookup functions
    :param outer_bool: Boolean operator to use between search terms
    :param inner_bool: Boolean operator to use between lookups
    :param term_operator: Term operator to use between field and a search term
    :attribute
    """

    def __init__(
        self,
        lookups: dict[str, callable] = None,
        outer_bool=BooleanOperators.AND,
        inner_bool=BooleanOperators.OR,
        term_operator=TermOperators.FUZZY,
    ):
        self.filter_fields = lookups
        self.outer_bool = outer_bool.value
        self.inner_bool = inner_bool.value
        self.term_operator = term_operator.value
        #: List of properties from CCURE to be included in the CCURE response
        self.display_properties = []

    def _compile_term(self, term) -> str:
        """Get all parts of the query for one search term"""
        fields = [(field_name, lookup(term)) for field_name, lookup in self.filter_fields.items()]
        field_queries = [f"{field_name} {self.term_operator} '{lookup}'" for field_name, lookup in fields]
        return f"({self.inner_bool.join(field_queries)})"

    def update_display_properties(self, properties: list[str]):
        if not isinstance(properties, list):
            raise TypeError("Properties must be a list of strings")
        self.display_properties += properties

    def filter(self, search):
        pass


class PersonnelFilter(BaseCcureFilter):
    """Basic CCure Personnel Filter
    :param lookups: Dict containing searchable field names and their lookup functions
    :param outer_bool: Boolean operator to use between search terms
    :param inner_bool: Boolean operator to use between lookups
    :param term_operator: Term operator to use between field and a search term
    :param display_properties: List of properties from CCure to be included in the CCure response
    :attribute
    """

    def __init__(
        self,
        lookups: Optional[dict[str, callable]] = None,
        outer_bool=BooleanOperators.AND,
        inner_bool=BooleanOperators.OR,
        term_operator=TermOperators.FUZZY,
        display_properties: Optional[list[str]] = None
    ):
        self.filter_fields = lookups or PERSONNEL_LOOKUP_FIELDS
        self.outer_bool = f" {outer_bool.value} "
        self.inner_bool = f" {inner_bool.value} "
        self.term_operator = term_operator.value
        self.display_properties = ["FirstName", "MiddleName", "LastName", "ObjectID"]
        if display_properties is not None:
            self.display_properties = display_properties

    def filter(self, search: list[str]) -> str:
        if not isinstance(search, list):
            raise TypeError("Search must be a list of strings")
        return self.outer_bool.join(self._compile_term(term) for term in search)


class ClearanceFilter(BaseCcureFilter):
    """Basic CCure Clearance Filter
    :param lookups: Dict containing searchable field names and their lookup functions
    :param outer_bool: Boolean operator to use between search terms
    :param inner_bool: Boolean operator to use between lookups
    :param term_operator: Term operator to use between field and a search term
    :param display_properties: List of properties from CCure to be included in the CCure response
    :attribute
    """

    def __init__(
        self,
        lookups: Optional[dict[str, callable]] = None,
        outer_bool=BooleanOperators.AND,
        inner_bool=BooleanOperators.OR,
        term_operator=TermOperators.FUZZY,
        display_properties: Optional[list[str]] = None
    ):
        self.filter_fields = lookups or CLEARANCE_LOOKUP_FIELDS
        self.outer_bool = f" {outer_bool.value} "
        self.inner_bool = f" {inner_bool.value} "
        self.term_operator = term_operator.value
        self.display_properties = ["Name"]
        if display_properties is not None:
            self.display_properties = display_properties

    def filter(self, search: list[str]) -> str:
        if not isinstance(search, list):
            raise TypeError("Search must be a list of strings")
        return self.outer_bool.join(self._compile_term(term) for term in search)


class CredentialFilter(BaseCcureFilter):
    """Basic CCure Credential Filter
    :param lookups: Dict containing searchable field names and their lookup functions
    :param outer_bool: Boolean operator to use between search terms
    :param inner_bool: Boolean operator to use between lookups
    :param term_operator: Term operator to use between field and a search term
    :param display_properties: List of properties from CCure to be included in the CCure response
    :attribute
    """

    def __init__(
        self,
        lookups: Optional[dict[str, callable]] = None,
        outer_bool=BooleanOperators.AND,
        inner_bool=BooleanOperators.OR,
        term_operator=TermOperators.FUZZY,
        display_properties: Optional[list[str]] = None
    ):
        self.filter_fields = lookups or CREDENTIAL_LOOKUP_FIELDS
        self.outer_bool = f" {outer_bool.value} "
        self.inner_bool = f" {inner_bool.value} "
        self.term_operator = term_operator.value
        self.display_properties = ["Name"]
        if display_properties is not None:
            self.display_properties = display_properties

    def filter(self, search: list) -> str:
        if not isinstance(search, list):
            raise TypeError("`search` must be a list of search terms")
        return self.outer_bool.join(self._compile_term(term) for term in search)


class ClearanceItemFilter(BaseCcureFilter):
    """Basic CCure ClearanceItem Filter
    :param lookups: Dict containing searchable field names and their lookup functions
    :param outer_bool: Boolean operator to use between search terms
    :param inner_bool: Boolean operator to use between lookups
    :param term_operator: Term operator to use between field and a search term
    :param display_properties: List of properties from CCure to be included in the CCure response
    :attribute
    """

    def __init__(
        self,
        lookups: Optional[dict[str, callable]] = None,
        outer_bool=BooleanOperators.AND,
        inner_bool=BooleanOperators.OR,
        term_operator=TermOperators.FUZZY,
        display_properties: Optional[list[str]] = None
    ):
        self.filter_fields = lookups or CREDENTIAL_LOOKUP_FIELDS
        self.outer_bool = f" {outer_bool.value} "
        self.inner_bool = f" {inner_bool.value} "
        self.term_operator = term_operator.value
        self.display_properties = ["Name"]
        if display_properties is not None:
            self.display_properties = display_properties

    def filter(self, search: list) -> str:
        if not isinstance(search, list):
            raise TypeError("`search` must be a list of search terms")
        return self.outer_bool.join(self._compile_term(term) for term in search)
