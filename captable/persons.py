"""For tracking legal persons"""
from __future__ import absolute_import

from .mixins import Snowflake

class Person(Snowflake):
    """Represents a *legal* person
    
    Args:
        name (str) - The name of this Person

    """
    def __init__(self, name):
        self.name = name


class NaturalPerson(Person):
    """Represents a natural (non-entity) person"""


class Entity(Person):
    """Corporations are people too, my friends"""


