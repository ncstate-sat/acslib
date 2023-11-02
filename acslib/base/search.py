from abc import ABC, abstractmethod
from connection import ACSConnection


class ACSSearch(ABC):
    """Base class for handling ACS searches"""

    def __init__(self, connection: ACSConnection, **kwargs):
        self.connection = connection
        self.logger = kwargs.get("logger")
        self.session_id = None
        self.results = []

    @abstractmethod
    def search(self):
        pass
