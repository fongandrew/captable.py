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
        txn_datetime (datetime): When this transaction occurred
        classes (list): List of dicts with a "cls" key pointing to a class
            of securities and an integer "amount" key indicating how many
            shares of that security to authorize 

    """
    def __init__(self, classes, txn_datetime=None):
        super(AuthTransaction, self).__init__(txn_datetime)
        for cls in classes:
            if not issubclass(cls["cls"], securities.Security):
                raise ValueError("Can only authorize subclasses of Security")
            if "amount" in cls:
                if type(cls["amount"]) != int:
                    raise ValueError("Can only authorize integer amounts")
            elif "delta" in cls:
                if type(cls["delta"]) != int:
                    raise ValueError("Can only authorize integer deltas")
            else:
                raise ValueError("Must specify amount or delta in "
                                 "AuthTransaction")
        self.classes = classes

    def process(self, state):
        "Processing an AuthTransaction means setting the amount to a set value"
        for cls in self.classes:
            amounts = state.get_amounts(cls["cls"])
            if "amount" in cls:
                amounts.authorized = cls["amount"]
            elif "delta" in cls:
                amounts.authorized += cls["delta"]

