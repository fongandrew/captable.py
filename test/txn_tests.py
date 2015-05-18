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
