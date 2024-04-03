from abc import ABC

from acslib.base import ACSConnection


class AccessControlSystem(ABC):
    """Base class for all ACS implementations"""

    def __init__(self, connection: ACSConnection):
        self.connection = connection

    # Abstract ACS methods
