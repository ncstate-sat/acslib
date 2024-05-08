from abc import ABC, abstractmethod
from enum import Enum


class BooleanOperators(Enum):
    AND = "AND"
    OR = "OR"


class TermOperators(Enum):
    EQUALS = "="
    FUZZY = "LIKE"


class ACSFilter(ABC):
    @abstractmethod
    def filter(self, search):
        pass
