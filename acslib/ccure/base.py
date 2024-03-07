from typing import Optional

from acslib.base import AccessControlSystem
from acslib.ccure.connection import CcureConnection


class CcureACS(AccessControlSystem):
    """."""

    def __init__(self, connection: Optional[CcureConnection] = None):
        """."""
        super().__init__(connection=connection)
        if not self.connection:
            self.connection = CcureConnection()
        self.logger = self.connection.logger
        self.request_options = {}
        self.search_filter = None

    @property
    def config(self):
        """."""
        return self.connection.config
