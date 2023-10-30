from abc import ABC, abstractmethod
from numbers import Number
from typing import Iterable


class ACSConnection:
    """Base class for handling ACS connections"""
    # TODO move handle_requests logic here

    scheduled_jobs = {
        "daily_jobs": [],
        "hourly_jobs": [],
        "minutely_jobs": [],
    }


class AccessControlSystem(ABC):
    """
    Base class for access control systems
    Not all methods will be used in all implementations
    """

    scheduled_jobs = {
        "daily_jobs": [],
        "hourly_jobs": [],
        "minutely_jobs": [],
    }

    # Abstract ACS methods

    @abstractmethod
    @classmethod
    def search_clearances(request_data: dict) -> list:
        """Base method for searching clearances"""

    @abstractmethod
    @classmethod
    def get_clearances_count(cls) -> int:
        """"Base method for getting a count of all clearances in the system"""

    @abstractmethod
    @classmethod
    def get_assigned_clearances(cls, assignee_id) -> list:
        """Base method to get clearances assigned to a person"""

    @abstractmethod
    @classmethod
    def get_clearance_by_id(cls, clearance_id) -> dict:
        """Base method to get one clearance"""

    @abstractmethod
    @classmethod
    def get_clearances_by_id(cls, clearance_ids: list) -> list[dict]:
        """Base method to get multiple clearanaces"""

    @abstractmethod
    @classmethod
    def get_clearance_name(cls, clearance_id) -> str:
        """Base method to get a clearance's name"""

    @abstractmethod
    @classmethod
    def get_clearance_names(cls, clearance_id: Iterable) -> str:
        """Base method to get clearances' names"""

    # @abstractmethod
    # @classmethod
    # def assign_clearances(cls, configs: list[dict]):
    #     """Base method to assign one or more clearances to one or more people"""

    # @abstractmethod
    # @classmethod
    # def revoke_clearances(cls, configs: list[dict]):
    #     """Base method to revoke one or more clearances to one or more people"""

    # @abstractmethod
    # @classmethod
    # def disable_person(cls, person_id):
    #     """Base method to set a disable flag on a person's record"""

    # @abstractmethod
    # @classmethod
    # def add_person(cls, property_names, property_values):
    #     """Base method to add a person to the database"""
    #     # TODO refactor. Args should be one dict, not two parallel lists

    @abstractmethod
    @classmethod
    def get_clearance_assignees(cls, clearance_ids, *args, **kwargs):
        """Base method to get lists of people assigned to the given clearances"""
