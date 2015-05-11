"""Transactions represent some modification of or addition to a captable
at some point in time.
"""
from __future__ import absolute_import

import datetime
from . import securities
from . import state


class Transaction(object):
    """A single transaction within a captable -- most used as a baseclass for
    other transacitons

    Args:
        txn_datetime (datetime): When this transaction occurred
    
    """
    def __init__(self, txn_datetime=None):
        self.datetime = txn_datetime or datetime.datetime.now()

    def process(self, state):
        raise NotImplementedError


class MultiTransaction(Transaction):
    "An object that combines multiple transactions into a single transaction"

    def __init__(self, txns, txn_datetime=None):
        # Validate first
        for txn in txns:
            if not isinstance(txn, Transaction):
                raise ValueError("MultiTransaction must consist only of "
                                 "instances of Transactions")

        super(MultiTransaction, self).__init__(txn_datetime)
        self.transactions = txns
        for txn in self.transactions:
            txn.datetime = self.datetime # Conform all datetimes

    def process(self, state):
        """Prcess all sub-transactions"""
        for txn in self.transactions:
            txn.process(state)


class AuthTransaction(Transaction):
    """Transaction authorizing a new security

    Args:
        txn_datetime (datetime): When this transaction occurred, optional
        cls (Security subclass): Subclass of Security that is being authorized
        amount (int): How many total shares to authorize -- replaces previous
            amount rather than increment it
        delta (int): Alternative to delta, how many shares to increment or 
            decrement authorized amount by. Either amount or delta may be
            set. If both are set, one can be used to sanity-check the other
            during processing.

    """
    def __init__(self, cls, amount=None, delta=None, txn_datetime=None):
        # Validation
        if not issubclass(cls, securities.Security):
            raise ValueError("Cls must be a subclass of Security")
        if type(amount) != int and type(delta) != int:
            raise ValueError("Must specify integer amount or delta in "
                             "AuthTransaction")

        super(AuthTransaction, self).__init__(txn_datetime)
        self.cls = cls
        self.amount = amount
        self.delta = delta

    def process(self, state):
        "Processing an AuthTransaction means setting the amount to a set value"
        amounts = state.get_amounts(self.cls)
        if self.amount:
            amounts.authorized = self.amount
        elif self.delta:
            amounts.authorized += self.delta

