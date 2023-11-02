from abc import ABC, abstractmethod
from numbers import Number
from typing import Iterable

from numbers import Number
from typing import Any, Callable, Optional

import requests
from fastapi import status
from pydantic import BaseModel, Field

from .handle_requests import RequestData, RequestException, RequestResponse, handle_request


class ACSConnection:
    """Base class for handling ACS connections"""

    def __init__(self):
        """."""
        self.scheduled_jobs = {
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
    def search_clearances(self, request_data: dict) -> list:
        """Base method for searching clearances"""

    @abstractmethod
    def get_clearances_count(self) -> int:
        """"Base method for getting a count of all clearances in the system"""

    @abstractmethod
    def get_assigned_clearances(self, assignee_id) -> list:
        """Base method to get clearances assigned to a person"""

    @abstractmethod
    def get_clearance_by_id(self, clearance_id) -> dict:
        """Base method to get one clearance"""
        # TODO fold this into search_clearances?

    @abstractmethod
    def get_clearances_by_id(self, clearance_ids: list) -> list[dict]:
        """Base method to get multiple clearanaces"""
        # TODO fold this into search_clearances?

    @abstractmethod
    def get_clearance_name(self, clearance_id) -> str:
        """Base method to get a clearance's name"""
        # TODO fold this into search_clearances?

    @abstractmethod
    def get_clearance_names(self, clearance_id: Iterable) -> str:
        """Base method to get clearances' names"""
        # TODO fold this into search_clearances?

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
    def get_clearance_assignees(self, clearance_ids, *args, **kwargs):
        """Base method to get lists of people assigned to the given clearances"""
