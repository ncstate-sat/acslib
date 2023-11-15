import pytest

from acslib.base.search import BooleanOperators, TermOperators
from acslib.ccure.search import (
    FUZZ,
    LFUZZ,
    NFUZZ,
    PERSONNEL_LOOKUP_FIELDS,
    RFUZZ,
    PersonnelFilter,
)


def test_default_instance():
    filter = PersonnelFilter()
    assert filter.filter_fields == PERSONNEL_LOOKUP_FIELDS
    assert filter.outer_bool == "AND"
    assert filter.inner_bool == "OR"
    assert filter.term_operator == "LIKE"
    assert filter.display_properties == ["FirstName", "MiddleName", "LastName"]


def test_custom_instance():
    filter = PersonnelFilter(
        lookups=[("Text1", NFUZZ), ("Tex14", NFUZZ)],
        outer_bool=BooleanOperators.OR,
        inner_bool=BooleanOperators.AND,
        term_operator=TermOperators.EQUALS,
    )
    assert filter.filter_fields == [("Text1", NFUZZ), ("Tex14", NFUZZ)]
    assert filter.outer_bool == "OR"
    assert filter.inner_bool == "AND"
    assert filter.term_operator == "="


def test_single_search_term():
    filter = PersonnelFilter()
    search = filter.filter(["test"])
    assert search == "(FirstName LIKE '%test%' OR LastName LIKE '%test%')"


def test_single_search_term_not_list():
    filter = PersonnelFilter()
    with pytest.raises(TypeError):
        filter.filter("test")


def test_multiple_terms():
    filter = PersonnelFilter()
    search = filter.filter(["test", "test2"])
    assert (
        search
        == "(FirstName LIKE '%test%' OR LastName LIKE '%test%') AND (FirstName LIKE '%test2%' OR LastName LIKE '%test2%')"
    )


def test_update_display_properties():
    filter = PersonnelFilter()
    filter.update_display_properties(["EmailAddress"])
    assert len(filter.display_properties) == 4
    assert "EmailAddress" in filter.display_properties


def test_update_display_properties_not_list():
    filter = PersonnelFilter()
    with pytest.raises(TypeError):
        filter.update_display_properties("EmailAddress")


def test_fuzz_functions():
    assert LFUZZ("test") == "%test"
    assert RFUZZ("test") == "test%"
    assert FUZZ("test") == "%test%"
    assert NFUZZ("test") == "test"
