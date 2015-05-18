"""For managing captable and companies
"""
from __future__ import absolute_import

from .logger import logger
from .state import CapTableState
from .validation import DEFAULT_VALIDATORS
import copy
import datetime

class CapTable(object):
    """Represents a cap table for a company. This is really a wrapper around
    CapTableState that handles transactional changes to the table."""

    def __init__(self, validators=DEFAULT_VALIDATORS):
        # List of 2-tuples containing the datetime and transaction of each
        # transaction successfully processed for this table
        self.transactions = []

        # A dict containing actual state data. All state information should
        # live here to make reversion easier.
        self.state = CapTableState()

        # Validators are called after each transaction recording to verify
        # state. Note that validators are called after all transactions in
        # a multi-transaction have been called.
        self.validators = validators

    @property
    def datetime(self):
        """What 'time' is the table currently at -- defaults to datetime of 
        last recorded transaction"""
        if self.transactions:
            return self.transactions[-1][0]
        return None

    def record(self, datetime_, txn):
        """Record a single transaction

        Args:
            datetime_ (datetime) - The date and time at which the transaction 
                occurs. Pass None to use current time.
            txn (callable) - A callable object that will be called with
                datetime_ and the current state of the captable. This callable
                should return the new, modified state.
        """
        if not callable(txn):
            raise ValueError("Transaction must be callable")

        if not datetime_:
            datetime_ = datetime.datetime.now()

        current = self.datetime
        if current and current > datetime_:
            raise ValueError("Cannot record transaction older that current "
                "captable state. Current datetime is %s, record call was for "
                "%s" % (repr(current), repr(datetime_)))

        # When processing transaction, pass a copy of state to simplify the
        # commit/rollback process.
        new_state = txn(datetime_, copy.deepcopy(self.state))

        # Make sure transaction remembered to return new state state
        if new_state == None:
            raise RuntimeError("Transaction did not return new state data")

        # Validate the new state
        for validate in self.validators:
            validate(new_state)

        # If txn succeeds, "commit" the return value as the new state
        self.state = new_state

        # Record actual transaction and datetime as 2-tuple
        self.transactions.append((datetime_, txn))

    def record_multi(self, datetime_, *txns):
        """Record multiple transactions as a single transaction"""
        if len(txns) == 0:
            raise ValueError("No transactions provided")
        self.record(datetime_, MultiTransaction(*txns))
        

class MultiTransaction(object):
    "An object that combines multiple transactions into a single transaction"
    def __init__(self, *txns):
        self.txns = txns

    def __call__(self, datetime_, state):
        """Prcess all sub-transactions"""
        for txn in self.txns:
            state = txn(datetime_, state)
            if state == None:
                raise RuntimeError("Transaction part did not return new "
                                   "state data")
        return state