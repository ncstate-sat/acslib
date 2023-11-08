from enum import Enum
from acslib.base.search import Filter

LFUZZ = lambda x: f"%{x}"
RFUZZ = lambda x: f"{x}%"
FUZZ = lambda x: f"%{x}%"

PERSONNEL_LOOKUP_FIELDS = [
    ('FirstName', FUZZ),
    ('LastName', FUZZ)
]


class SearchTypes(Enum):
    PERSONNEL = "personnel"


class PersonnelFilter(Filter):

    def __init__(self, lookups=None):
        super().__init__(lookups=lookups)

    def _compile_term(self, term: str) -> str:
        accumulator = ""
        for i, lookup in enumerate(self.filter_fields):
            if not i:
                accumulator += f"({lookup[0]} LIKE '{lookup[1](term)}' "
            else:
                accumulator += f"OR {lookup[0]} LIKE '{lookup[1](term)}' "
        accumulator = accumulator.rstrip()
        accumulator += ")"
        return accumulator

    def filter(self, search):
        search_filter = ""
        for term in search.split():
            search_filter += self._compile_term(term) + " AND "
        return search_filter.rstrip(" AND ")
