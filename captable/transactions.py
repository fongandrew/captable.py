"""Transactions represent some modification of or addition to a captable
at some point in time.
"""
from __future__ import absolute_import
from . import securities
from . import state

class Transaction(object):
    """
    A single transaction within a captable -- most used as a baseclass for
    other transacitons

    Args:
        txn_datetime (datetime): When this transaction occurred
    
    """
    def __init__(self, txn_datetime):
        self.datetime = txn_datetime


class AuthTransaction(Transaction):
    """
    Transaction authorizing a new security

    Parameters
    ----------
    Args:
        txn_datetime (datetime): When this transaction occurred
        classes (list): List of dicts with a "cls" key pointing to a class
            of securities and an integer "amount" key indicating how many
            shares of that security to authorize 
    classes (list): List of dicts mapping 
    """
    def __init__(self, txn_datetime, classes):
        super(AuthTransaction, self).__init__(txn_datetime)
        for cls in classes:
            print cls;
            if not issubclass(cls["cls"], securities.Security):
                raise ValueError("Can only authorize subclasses of Security")
            if type(cls["amount"]) != int:
                raise ValueError("Can only authorize integer amounts")
        self.classes = classes

    def process(self, state):
        "Processing an AuthTransaction means setting the amount to a set value"
        for cls in self.classes:
            security_type = cls["cls"]
            amount = cls["amount"]
            state.get_amounts(security_type.name).authorized = amount
