"""For tracking captable state at a particular point in time
"""
from __future__ import absolute_import

class CapTableState(object):
    """Represents a captable at a particular point in time

    Properties:
        securities (dict): A dict mapping the name of a class of securities to
            a SecuritiesState instance
    """
    def __init__(self):
        # Dict mapping securities names to amounts outstanding and issued
        self.securities = {};

    def get_amounts(self, name):
        return self.securities.setdefault(name, SecuritiesState())


class SecuritiesState(object):
    """Represents the state of a particular class of captable securities

    Properties:
        authorized (integer) - Total number of shares of this security 
        issued - Total number of shares of this security issued to 
            parties (which may or may not be outstanding)
        outstanding - Total number of shares issued and outstanding
        reserved - Total number of shares reserved for future issuance
    """
    def __init__(self, authorized=0, issued=0, outstanding=0, reserved=0):
        self.authorized = authorized
        self.issued = issued
        self.outstanding = outstanding
        self.reserved = reserved
