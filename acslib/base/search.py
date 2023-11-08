from abc import ABC, abstractmethod


class Filter(ABC):
    def __init__(self, lookups: list[tuple]):
        self.filter_fields = lookups

    @abstractmethod
    def filter(self, search):
        pass




