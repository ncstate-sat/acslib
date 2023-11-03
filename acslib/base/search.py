from abc import ABC


class ACSSearchResult(ABC):
    """Base class for encapsulating search results"""

    def __init__(self):
        self.results = []

    def __iter__(self):
        return iter(self.results)

    def __len__(self):
        return len(self.results)

    def __getitem__(self, item: int):
        return self.results[item]
