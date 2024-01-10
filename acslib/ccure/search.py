from enum import Enum

from acslib.base.search import ACSFilter, BooleanOperators, TermOperators


def left_fuzz(term):
    return f"'%{term}'"


def right_fuzz(term):
    return f"'{term}%'"


def full_fuzz(term):
    return f"'%{term}%'"


def no_fuzz(term):
    return f"'{term}'"


LFUZZ = left_fuzz
RFUZZ = right_fuzz
FUZZ = full_fuzz
NFUZZ = no_fuzz

PERSONNEL_LOOKUP_FIELDS = [("FirstName", FUZZ), ("LastName", FUZZ)]
CLEARANCE_LOOKUP_FIELDS = {"Name": FUZZ, "ObjectID": NFUZZ}


class SearchTypes(Enum):
    PERSONNEL = "personnel"
    CLEARANCE = "clearance"


class BaseCcureFilter(ACSFilter):
    """Base CCure Filter
    :param lookups: List of tuples containing the field name and the lookup function
    :param outer_bool: Boolean operator to use between search terms
    :param inner_bool: Boolean operator to use between lookups
    :param term_operator: Term operator to use between field and a search term
    :attribute
    """

    def __init__(
        self,
        lookups: list[tuple[str, callable]] = None,
        outer_bool=BooleanOperators.AND,
        inner_bool=BooleanOperators.OR,
        term_operator=TermOperators.FUZZY,
    ):
        self.filter_fields = lookups
        self.outer_bool = outer_bool.value
        self.inner_bool = inner_bool.value
        self.term_operator = term_operator.value
        #: List of properties from CCURE to be included in the CCURE response
        self.display_properties = ["FirstName", "MiddleName", "LastName", "ObjectID"]

    def _compile_term(self, term: str) -> str:
        accumulator = ""
        for i, lookup in enumerate(self.filter_fields):
            if not i:
                accumulator += f"({lookup[0]} {self.term_operator} '{lookup[1](term)}' "
            else:
                accumulator += (
                    f"{self.inner_bool} {lookup[0]} {self.term_operator} '{lookup[1](term)}' "
                )
        accumulator = accumulator.rstrip() + ")"
        return accumulator

    def _compile_term2(self, term: str) -> str:
        """Get all parts of the query for one search term"""
        fields = [(field_name, lookup(term)) for field_name, lookup in self.filter_fields.items()]
        field_queries = [f"{field_name} {self.term_operator} {lookup}" for field_name, lookup in fields]
        return f"({self.inner_bool.join(field_queries)})"

    def update_display_properties(self, properties: list[str]):
        if not isinstance(properties, list):
            raise TypeError("Properties must be a list of strings")
        self.display_properties += properties

    def filter(self, search):
        pass


class PersonnelFilter(BaseCcureFilter):
    """Basic CCure Personnel Filter
    :param lookups: List of tuples containing the field name and the lookup function
    :param outer_bool: Boolean operator to use between search terms
    :param inner_bool: Boolean operator to use between lookups
    :param term_operator: Term operator to use between field and a search term
    :attribute
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.filter_fields:
            self.filter_fields = PERSONNEL_LOOKUP_FIELDS
        self.display_properties = ["FirstName", "MiddleName", "LastName"]

    def filter(self, search: list[str]) -> str:
        if not isinstance(search, list):
            raise TypeError("Search must be a list of strings")
        search_filter = ""
        for term in search:
            search_filter += self._compile_term(term) + f" {self.outer_bool} "
        return search_filter.rstrip(f" {self.outer_bool} ")


class ClearanceFilter(BaseCcureFilter):
    """Basic CCure Clearance Filter
    :param lookups: List of tuples containing the field name and the lookup function
    :param outer_bool: Boolean operator to use between search terms
    :param inner_bool: Boolean operator to use between lookups
    :param term_operator: Term operator to use between field and a search term
    :attribute
    """

    def __init__(
        self,
        lookups: dict[str, callable] = [],
        outer_bool=BooleanOperators.AND,
        inner_bool=BooleanOperators.OR,
        term_operator=TermOperators.FUZZY,
    ):
        self.filter_fields = lookups if lookups else CLEARANCE_LOOKUP_FIELDS
        self.outer_bool = f" {outer_bool.value} "
        self.inner_bool = f" {inner_bool.value} "
        self.term_operator = term_operator.value
        # List of properties from CCURE to be included in the CCURE response
        self.display_properties = ["Name"]

    def filter(self, search: list[str]) -> str:
        if not isinstance(search, list):
            raise TypeError("Search must be a list of strings")
        return self.outer_bool.join(self._compile_term2(term) for term in search)
