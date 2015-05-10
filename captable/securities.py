"""For tracking the different types and classes of securities in a table
"""
from __future__ import absolute_import

class Security(object):
    @property
    def name(self):
        "Human-readable name for this class or type of security"
        raise NotImplementedError

class Stock(Security):
    pass

class CommonStock(Stock):
    name = "Common Stock"