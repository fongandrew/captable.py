from __future__ import absolute_import

import captable
import unittest
import datetime
import pytest
from ._helpers import StubTransaction


class TransactionTests(unittest.TestCase):
    """Test adding transactions and processing them"""

    def setUp(self):
        """Initialize a blank captable and authorize multiple classes of
        securities"""
        self.table = captable.CapTable()
        self.txn_1 = StubTransaction(txn_datetime=datetime.datetime(2015,5,1))
        self.txn_2 = StubTransaction(txn_datetime=datetime.datetime(2015,5,2))
        self.txn_3 = StubTransaction(txn_datetime=datetime.datetime(2015,5,3))

        # NB: Order added shouldn't matter -- should sort based on time
        self.table.record_txn(self.txn_1)
        self.table.record_txn(self.txn_3)
        self.table.record_txn(self.txn_2)

    def test_transactions_list(self):
        """All transactions should be stored in table list"""
        self.assertEqual(self.table.transactions,
                         [self.txn_1, self.txn_2, self.txn_3])

    def test_process_all(self):
        """Calling process without an argument processes all transactions"""
        state = self.table.process()
        StubTransaction.check(state, self.txn_1, self.txn_2, self.txn_3)

    def test_process_to_time(self):
        """Calling process with a datetime should process transactions up to
        (and including) that exact time"""
        state = self.table.process(datetime.datetime(2015, 5, 2))
        StubTransaction.check(state, self.txn_1, self.txn_2)


class ErrorTransaction(StubTransaction):
    """Simulates an exception raised after state changes"""
    def process(self, state):
        super(ErrorTransaction, self).process(state)
        raise RuntimeError("Boom")

def test_rollback():
    """Test that throwing an error roll backs the transaction"""
    table = captable.CapTable()
    txn_1 = StubTransaction(txn_datetime=datetime.datetime(2015,5,1))
    txn_2 = ErrorTransaction(txn_datetime=datetime.datetime(2015,5,2))
    txn_3 = StubTransaction(txn_datetime=datetime.datetime(2015,5,3))

    table.record_txn(txn_1)
    table.record_txn(txn_2)
    table.record_txn(txn_3)

    state = table.process(quiet_errors=True)

    # Check that a warning was logged
    assert len(state.warnings) == 1
    
    # Only txn1 should have processed
    StubTransaction.check(state, txn_1)

