"""For managing captable and companies
"""
from __future__ import absolute_import
from . import transactions
from . import state

class CapTable(object):
    """Represents a captable for a company -- functions as a list of
    transactions for all intents and purposes"""
    
    def __init__(self, *args):
        """Can be constructed with a list of initial security types"""
        # List of all transactions within this table
        self.transactions = []

    def record_txn(self, txn):
        """Record a single transaction"""
        if (not isinstance(txn, transactions.Transaction)):
            raise ValueError("Can only record transactions"
                             "of Transaction class")

        # TODO: sort transacitons list by time
        self.transactions.append(txn)

    def process(self, to_time=None):
        """Process transactions up to (and including) a particular time and 
        returns date as of that time"""
        tableState = state.CapTableState();

        # TODO: Process only to to_time
        for txn in self.transactions:
            txn.process(tableState)
        return tableState;

    def authorize(self, *args, **kwds):
        txn = transactions.AuthTransaction(*args, **kwds)
        self.record_txn(txn)

