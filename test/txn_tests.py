from __future__ import absolute_import

import captable
import datetime
import pytest
from ._helpers import StubTransaction, ErrorTransaction


def test_record():
    """Recording transactions should modify state"""
    table = captable.CapTable()
    txn_1 = StubTransaction()
    txn_2 = StubTransaction()
    txn_3 = StubTransaction()

    table.record(datetime.datetime(2015, 5, 1), txn_1)
    table.record(datetime.datetime(2015, 5, 2), txn_2)
    table.record(datetime.datetime(2015, 5, 3), txn_3)

    # Check that table has list of transactions and times recorded
    assert table.transactions == [
        (datetime.datetime(2015, 5, 1), txn_1),
        (datetime.datetime(2015, 5, 2), txn_2),
        (datetime.datetime(2015, 5, 3), txn_3)
    ]

    # Check that each transaction modified state
    StubTransaction.check(table.state, txn_1, txn_2, txn_3)

def test_forward_time_only():
    """Should not be able to record past transactions but should be able to
    record identically timed transactions"""
    table = captable.CapTable()
    txn_1 = StubTransaction()
    txn_2 = StubTransaction()

    table.record(datetime.datetime(2015, 5, 1), txn_1)
    table.record(datetime.datetime(2015, 5, 1), txn_2)

    # Check that each transaction modified state
    StubTransaction.check(table.state, txn_1, txn_2)

    txn_3 = StubTransaction()
    with pytest.raises(ValueError):
        table.record(datetime.datetime(2015, 4, 1), txn_3)

def test_rollback():
    """Failed transaction should not modify state"""
    table = captable.CapTable()
    txn_1 = StubTransaction()
    txn_2 = ErrorTransaction()

    with pytest.raises(RuntimeError):
        table.record(datetime.datetime(2015, 5, 1), txn_1)
        table.record(datetime.datetime(2015, 5, 2), txn_2)
    
    # Only txn1 should have processed
    assert table.transactions == [
        (datetime.datetime(2015, 5, 1), txn_1)
    ]
    StubTransaction.check(table.state, txn_1)


# class TransactionTests(unittest.TestCase):
#     """Test adding transactions and processing them"""

#     def setUp(self):
#         """Initialize a blank captable and authorize multiple classes of
#         securities"""
#         self.table = captable.CapTable()
#         self.txn_1 = StubTransaction(txn_datetime=datetime.datetime(2015,5,1))
#         self.txn_2 = StubTransaction(txn_datetime=datetime.datetime(2015,5,2))
#         self.txn_3 = StubTransaction(txn_datetime=datetime.datetime(2015,5,3))

#         # NB: Order added shouldn't matter -- should sort based on time
#         self.table.record_txn(self.txn_1)
#         self.table.record_txn(self.txn_3)
#         self.table.record_txn(self.txn_2)

#     def test_transactions_list(self):
#         """All transactions should be stored in table list"""
#         self.assertEqual(self.table.transactions,
#                          [self.txn_1, self.txn_2, self.txn_3])

#     def test_process_all(self):
#         """Calling process without an argument processes all transactions"""
#         state = self.table.process()
#         StubTransaction.check(state, self.txn_1, self.txn_2, self.txn_3)

#     def test_process_to_time(self):
#         """Calling process with a datetime should process transactions up to
#         (and including) that exact time"""
#         state = self.table.process(datetime.datetime(2015, 5, 2))
#         StubTransaction.check(state, self.txn_1, self.txn_2)

# def test_rollback():
#     """Test that throwing an error roll backs the transaction"""
#     table = captable.CapTable()
#     txn_1 = StubTransaction(txn_datetime=datetime.datetime(2015,5,1))
#     txn_2 = ErrorTransaction(txn_datetime=datetime.datetime(2015,5,2))
#     txn_3 = StubTransaction(txn_datetime=datetime.datetime(2015,5,3))

#     table.record_txn(txn_1)
#     table.record_txn(txn_2)
#     table.record_txn(txn_3)

#     state = table.process(quiet_errors=True)

#     # Check that a warning was logged
#     assert len(state.warnings) == 1
    
#     # Only txn1 should have processed
#     StubTransaction.check(state, txn_1)

# def test_ignore():
#     """Test that we can process with ignored errors"""
#     table = captable.CapTable()
#     txn_1 = StubTransaction(txn_datetime=datetime.datetime(2015,5,1))
#     txn_2 = ErrorTransaction(txn_datetime=datetime.datetime(2015,5,2))
#     txn_3 = StubTransaction(txn_datetime=datetime.datetime(2015,5,3))

#     table.record_txn(txn_1)
#     table.record_txn(txn_2)
#     table.record_txn(txn_3)

#     state = table.process(ignore_errors=True)

#     # Check that a warning was logged
#     assert len(state.warnings) == 1
    
#     # Txn2 should have been ignored
#     StubTransaction.check(state, txn_1, txn_3)

