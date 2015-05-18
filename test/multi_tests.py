from __future__ import absolute_import

import captable
import datetime
import pytest
from ._helpers import StubTransaction, ErrorTransaction

def test_multi_txn():
    """Should be able to combine multiple transactions into a single 
    transaction"""
    table = captable.CapTable()
    txn_1 = StubTransaction()
    txn_2 = StubTransaction()
    table.record_multi(datetime.datetime(2015,5,1), txn_1, txn_2)

    # Only two transactions recorded
    assert len(table.transactions) == 1

    # Check proper class on multi-txn
    dt, txn = table.transactions[0]
    assert dt == datetime.datetime(2015,5,1)
    assert isinstance(txn, captable.MultiTransaction)

    # Both transactions should have processed
    StubTransaction.check(table.state, txn_1, txn_2)

def test_multi_txn_rollback():
    """Multi transaction should rollback all if any has error"""
    table = captable.CapTable()
    txn_1 = StubTransaction()
    txn_2 = ErrorTransaction()
    with pytest.raises(RuntimeError):
        table.record_multi(datetime.datetime(2015,5,1), txn_1, txn_2)

    # Neither txn_1 nor txn_2 should have processed
    assert len(table.transactions) == 0
    StubTransaction.check(table.state)