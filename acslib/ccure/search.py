from enum import Enum
from acslib.base.search import ACSFilter, BooleanOperators, TermOperators


def left_fuzz(term):
    return f"%{term}"


def right_fuzz(term):
    return f"{term}%"


def full_fuzz(term):
    return f"%{term}%"


def no_fuzz(term):
    return term


LFUZZ = left_fuzz
RFUZZ = right_fuzz
FUZZ = full_fuzz
NFUZZ = no_fuzz


PERSONNEL_LOOKUP_FIELDS = [
    ('FirstName', FUZZ),
    ('LastName', FUZZ)
]


class SearchTypes(Enum):
    PERSONNEL = "personnel"


class PersonnelFilter(ACSFilter):

    def __init__(
        self,
        lookups: list[tuple[str, callable]] = None,
        outer_bool=BooleanOperators.AND,
        inner_bool=BooleanOperators.OR,
        term_operator=TermOperators.FUZZY
    ):

        self.filter_fields = lookups if lookups else PERSONNEL_LOOKUP_FIELDS
        self.outer_bool = outer_bool.value
        self.inner_bool = inner_bool.value
        self.term_operator = term_operator.value
        self.display_properties = ["FirstName", "MiddleName", "LastName"]

    def _compile_term(self, term: str) -> str:
        accumulator = ""
        for i, lookup in enumerate(self.filter_fields):
            if not i:
                accumulator += f"({lookup[0]} {self.term_operator} '{lookup[1](term)}' "
            else:
                accumulator += f"{self.inner_bool} {lookup[0]} {self.term_operator} '{lookup[1](term)}' "
        accumulator = accumulator.rstrip() + ")"
        return accumulator

    def update_display_properties(self, properties: list[str]):
        self.display_properties += properties

    def filter(self, search: list[str]) -> str:
        if not isinstance(search, list):
            raise TypeError("Search must be a list of strings")
        search_filter = ""
        for term in search:
            search_filter += self._compile_term(term) + f" {self.outer_bool} "
        return search_filter.rstrip(f" {self.outer_bool} ")
