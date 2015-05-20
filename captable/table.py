"""For managing captable and companies
"""
from __future__ import absolute_import

from .logger import logger
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
        self.state = {}

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

    def record(self, datetime_, *txns):
        """Record a single transaction

        Args:
            datetime_ (datetime) - The date and time at which the transaction 
                occurs. Pass None to use current time.
            txns (list) - List of callables that will be called with
                datetime_ and the current state of the captable. Each callable
                should return the new, modified state. If more than one
                callable, will be recorded as a single transaction that all
                succeed or fail together.
        """
        if len(txns) == 0:
            raise ValueError("Must provide at least one transaction")

        if not datetime_:
            datetime_ = datetime.datetime.now()

        current = self.datetime
        if current and current > datetime_:
            raise ValueError("Cannot record transaction older that current "
                "captable state. Current datetime is %s, record call was for "
                "%s" % (repr(current), repr(datetime_)))

        # When processing transactions, pass a copy of state to simplify the 
        # commit/rollback process.
        new_state = copy.deepcopy(self.state)

        # Process all transactions. 
        for txn in txns:
            if not callable(txn):
                raise ValueError("Transaction must be callable")

            new_state = txn(datetime_, new_state)

            # Make sure transaction remembered to return new state state
            if new_state == None:
                raise RuntimeError("Transaction did not return new state data")

        # Validate the new state
        for validate in self.validators:
            validate(new_state)

        # If txn succeeds, "commit" the return value as the new state
        self.state = new_state

        # Record actual transactions and datetime as 2-tuple (or more if
        # multiple transactions)
        self.transactions.append((datetime_,) + txns)

    def __getitem__(self, key):
        """Shortcut for accessing the table's current state dict. If the key
        is an object with a '__table_key__' method, will pass current state to
        method for returning an object
        """
        if hasattr(key, '__table_key__'):
            return key.__table_key__(self.state)
        raise KeyError("%s does not have a '__table_key__' method" % repr(key))
