"""For tracking the different types and classes of securities in a table
"""
from __future__ import absolute_import

from . import mixins


class Security(mixins.Snowflake):
    """Represents a class or type of Security

    Args:
        name (str) - The name of this security, e.g. "Class A Common Stock"
    """

    def __init__(self, name):
        self.name = name

class Stock(Security):
    pass

class CommonStock(Stock):
    def __init__(self, name="Common Stock"):
        super(CommonStock, self).__init__(name)
