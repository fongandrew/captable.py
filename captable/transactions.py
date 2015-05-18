"""Transactions represent some modification of or addition to a captable
at some point in time.
"""
from __future__ import absolute_import

import datetime
from . import mixins
from . import securities
from . import state


class Transaction(mixins.Snowflake):
    """A single transaction within a captable -- most used as a baseclass for
    other transactions

    Args:
        txn_datetime (datetime): When this transaction occurred
    
    """
    def __init__(self, txn_datetime=None):
        self.datetime = txn_datetime or datetime.datetime.now()

    def __str__(self):
        return self.__class__.__name__ + " @ " + str(self.datetime)


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

    def __call__(self, state):
        """Prcess all sub-transactions"""
        for txn in self.transactions:
            txn(state)


class AuthTransaction(Transaction):
    """Transaction authorizing a new security

    Args:
        txn_datetime (datetime): When this transaction occurred, optional
        security (Security): Subclass of Security that is being authorized
        amount (int): How many total shares to authorize -- replaces previous
            amount rather than increment it
        delta (int): Alternative to delta, how many shares to increment or 
            decrement authorized amount by. Either amount or delta may be
            set. If both are set, one can be used to sanity-check the other
            during processing.

    """
    def __init__(self, security, amount=None, delta=None, txn_datetime=None):
        # Validation
        if not isinstance(security, securities.Security):
            raise ValueError("Cls must be an instance of Security")
        if type(amount) != int and type(delta) != int:
            raise ValueError("Must specify integer amount or delta in "
                             "AuthTransaction")

        super(AuthTransaction, self).__init__(txn_datetime)
        self.security = security
        self.amount = amount
        self.delta = delta

    def __call__(self, state):
        "Processing an AuthTransaction means setting the amount to a set value"
        security_state = state.get_security_state(self.security)
        if self.amount:
            security_state.authorized = self.amount
        elif self.delta:
            security_state.authorized += self.delta

