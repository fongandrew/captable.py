from __future__ import absolute_import

import captable
import datetime
from ._helpers import StubTransaction

def test_multi_txn():
    """Should be able to combine multiple transactions into a single 
    transaction"""
    table = captable.CapTable()
    txn_1 = StubTransaction()
    txn_2 = StubTransaction()
    table.record_multi_txn(txns=[txn_1, txn_2],
                           txn_datetime=datetime.datetime(2015,5,1))
    txn_3 = StubTransaction(txn_datetime=datetime.datetime(2015,5,2))
    table.record_txn(txn_3)

    # Only two transactions recorded
    assert len(table.transactions) == 2

    # Check proper class on multi-txn
    multi_txn = table.transactions[0]
    assert isinstance(multi_txn, captable.MultiTransaction)

    # The txn_datetime on the multi should supersede the individual times on 
    # either txn_1 or txn_2
    assert txn_1.datetime == datetime.datetime(2015,5,1)
    assert txn_2.datetime == datetime.datetime(2015,5,1)
    assert multi_txn.datetime == datetime.datetime(2015,5,1)
    assert list(multi_txn.transactions) == [txn_1, txn_2]

    # Processing should respect multi transaction datetimes
    state = table.process(datetime.datetime(2015,5,1))
    StubTransaction.check(state, txn_1, txn_2)
