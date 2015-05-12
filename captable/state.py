"""For tracking captable state at a particular point in time
"""
from __future__ import absolute_import

from .mixins import EqualityMixin
import copy


class CapTableState(EqualityMixin):
    """Represents a captable at a particular point in time

    Properties:
        securities (dict): A dict mapping the name of a class of securities to
            a SecuritiesState instance
        warnings (list): List of warnings tracked while processing
        last_txn (Transaction): Last transaction to process this state. Should
            be set by CapTable.process
    """
    def __init__(self):
        self.securities = {}
        self.warnings = []
        self.last_txn = None

    def copy(self):
        """Returns shallow-ish copy of state -- smart enough to make an
        additional shallow copy of built-in compound types"""
        ret = self.__class__()

        # Create shallow copies of each of this state's non-private attributes
        #   
        # (to make equality easier). Shallow is OK because each of the 
        # individual elements within each list or dict should be immutable
        for name, value in vars(self).iteritems():
            if not name.startswith("_"):
                if (isinstance(value, list) or 
                    isinstance(value, dict) or
                    isinstance(value, tuple)):
                    value = copy.copy(value)
                setattr(ret, name, value)

        return ret

    def warn(self, msg):
        warning = TransactionWarning(self.last_txn, msg, self)
        self.warnings.append(warning)

    def get_amounts(self, cls):
        return self.securities.setdefault(cls, SecuritiesState())


class SecuritiesState(EqualityMixin):
    """Represents the state of a particular class of captable securities

    Args:
        authorized (integer) - Optional number of shares of this security,
            defaults to 0
        issued - Optional number of shares of this security issued to 
            parties (which may or may not be outstanding), defaults to 0
        outstanding - Optional number of shares issued and outstanding,
            defaults to 0
        reserved - Optional number of shares reserved for future issuance,
            defaults to 0

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


class TransactionWarning(object):
    """Non-fatal indication that something is wrong with the current captable
    state. Processing can still proceed, but this should be checked.

    Args:
        txn (Transaction) - The transaction triggering this warning
        msg (str) - A message explaining the reason for the warning
        state (CapTableState) - The current CapTable state

    Properties:
        txn (Transaction) - The transaction triggering this warning
        msg (str) - A message explaining the reason for the warning
        state (CapTableState) - A copy of the CapTable state at the time the
            warning is created
    """
    def __init__(self, txn, msg, state):
        self.txn = txn
        self.msg = msg
        self.state = state.copy()