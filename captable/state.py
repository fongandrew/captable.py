"""For tracking captable state at a particular point in time
"""
from __future__ import absolute_import

from .mixins import EqualityMixin
import copy


class CapTableState(EqualityMixin):
    """Represents a captable at a particular point in time

    Properties:
        securities (dict): A dict mapping an instance of Securities to
            a SecuritiesState instance
        warnings (list): List of warnings tracked while processing
        last_txn (Transaction): Last transaction to process this state. Should
            be set by CapTable.process
    """
    def __init__(self):
        self.securities = {}
        self.warnings = []
        self.last_txn = None

    def warn(self, msg):
        warning = TransactionWarning(self.last_txn, msg, self)
        self.warnings.append(warning)

    def get_amounts(self, security):
        return self.securities.setdefault(security, SecuritiesState())


class SecuritiesState(EqualityMixin):
    """Represents the state of a particular class of captable securities

    Args:
        authorized (int) - Total number of shares of this security to authorize
        reissue (bool) - Can retired stock be reissued? Defaults to true
            per DGCL 243.

    Properties:
        authorized (int) - Total number of authorized shares
        issuances (list) - List of all issuances of this security
        reservations (list) - List of all reservations of this security
    """
    def __init__(self, authorized, reissue=True):
        self.authorized = authorized
        self.issuances = []
        self.reservations = []
        self.retirements = []
        self.reissue = reissue

    @property
    def outstanding(self):
        """Number of shares issued and outstanding"""
        return 0 #TODO

    @property
    def issued(self):
        """Number of shares issued, which may or may not be outstanding"""
        return 0 #TODO

    @property
    def reserved(self):
        """Number of shares reserved for later issuance"""
        return 0 #TODO
        
    @property
    def issuable(self):
        """Number of shares available for issuance"""
        ret = self.authorized - self.outstanding - self.retired
        return ret
    
    @property
    def unreserved(self):
        """Number of shares avilable for issuance after taking into account
        reserved shares"""
        return self.issuable - self.reserved

    def auth(self, total=None, delta=None):
        if (total != None):
            self.authorized = total
        elif (delta != None):
            self.authorized += delta

    def issue(self, shares, txn): #TODO
        pass

    def reserve(self, shares, txn): #TODO
        pass

    def retire(self, shares, txn): #TODO
        if self.reissue: 
            # If allowed to re-issued retired shares, then retired shares 
            # should resume the status of authorized and unissued shares
            pass

        else:
            # Retirement reduces the number of authorized
            pass 


class Issuance(object): #TODO
    """An issuance to a Person
    """
    def __init__(self, person, cls, amount, cert_no=None):
        pass


class Reservation(object): #TODO
    """A reservation of some amount of amount and class and stock for some
    future purpose"""
    pass


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
        self.state = copy.deepcopy(state)