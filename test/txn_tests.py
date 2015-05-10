from __future__ import absolute_import

import captable
import unittest
import datetime

class StubTransaction(captable.Transaction):
    """
    Helper used for testing purposes
    """
    def process(self, state):
        if not hasattr(state, "stubs_processed"):
            state.stubs_processed = []
        state.stubs_processed.append(self);


class TransactionTests(unittest.TestCase):
    """Test adding transacitons and processing them"""

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

    def check_process_order(self, state, *txns):
        def get_dt(txn):
            return txn.datetime
        expected = map(get_dt, txns)
        actual = map(get_dt, state.stubs_processed)
        self.assertEqual(expected, actual)

    def test_process_all(self):
        """Calling process without an argument processes all transactions"""
        state = self.table.process()
        self.check_process_order(state, self.txn_1, self.txn_2, self.txn_3)

    def test_process_to_time(self):
        """Calling process with a datetime should process transactions up to
        (and including) that exact time"""
        state = self.table.process(datetime.datetime(2015, 5, 2))
        self.check_process_order(state, self.txn_1, self.txn_2)
