from abc import ABC, abstractmethod


class ACSConfigException(Exception):
    pass


class ACSConfig(ABC):
    @abstractmethod
    def connection_data(self):
        pass
