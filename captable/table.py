"""For managing captable and companies
"""
from __future__ import absolute_import

from .logger import logger
from . import transactions
from . import state
import datetime
import copy

class CapTable(object):
    """Represents a captable for a company -- functions as a list of
    transactions for all intents and purposes
    """ 
    def __init__(self):
        """Can be constructed with a list of initial security types"""
        # List of all transactions within this table
        self.transactions = []

    def record_txn(self, txn):
        """Record a single transaction"""
        if (not isinstance(txn, transactions.Transaction)):
            raise ValueError("Can only record transactions"
                             "of Transaction class")
        self.transactions.append(txn)
        self.transactions.sort(key=(lambda txn: txn.datetime))

    def record_multi_txn(self, txns, txn_datetime=None):
        """Record multiple transactions"""
        multi_txn = transactions.MultiTransaction(
            txns=txns,
            txn_datetime=txn_datetime
        )
        self.record_txn(multi_txn)

    def process(self, table_state=None, to_time=None, quiet_errors=False):
        """Process transactions up to (and including) a particular time and 
        returns date as of that time"""

        # If only arg is a datetime, treat as datetime instead of state
        if to_time == None and isinstance(table_state, datetime.datetime):
            to_time = table_state
            table_state = None

        if not table_state: # Set table state to default
            table_state = state.CapTableState()
        elif not isinstance(table_state, state.CapTableState):
            raise ValueError("table_state should be CapTableState object")

        # Process only to to_time (assumes self.transactions is ordered)
        for txn in self.transactions:
            if (not to_time) or (txn.datetime <= to_time):
                logger.debug("Processing " + str(txn))

                # Create a copy before initating processing
                copy_state = copy.deepcopy(table_state)

                copy_state.last_txn = txn
                try:
                    txn.process(copy_state)

                    # If no exceptions, make the current state the next
                    # processing state
                    table_state = copy_state

                except Exception, e:
                    table_state.warn(e)
                    if quiet_errors:
                        break # Stop execution but don't fail
                    else:
                        raise # Just re-raise
            else:
                break
        return table_state;
