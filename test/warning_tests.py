from __future__ import absolute_import

import captable
import datetime
from ._helpers import StubTransaction

class WarningTxn(StubTransaction):
    def process(self, state):
        state.warn("I warned you!")
        super(WarningTxn, self).process(state)

def test_warn_txn():
    """Warning transactions should log warnings but not stop processing"""
    table = captable.CapTable()
    txn_1 = WarningTxn(datetime.datetime(2015,1,1))
    txn_2 = WarningTxn(datetime.datetime(2015,1,2))
    table.record_txn(txn_1)
    table.record_txn(txn_2)
    
    state = table.process()
    assert len(state.warnings) == 2

    # Actual current state has both processed, despite warnings
    StubTransaction.check(state, txn_1, txn_2)

    # First warning > copy of state AT warning 1 should not include any
    # any processing
    warning1 = state.warnings[0]
    assert warning1.txn == txn_1
    assert warning1.msg == "I warned you!"
    assert warning1.state.last_txn == txn_1
    StubTransaction.check(warning1.state)

    # Second warning > copy of state AT warning 2, includes processing from
    # first WarningTxn
    warning2 = state.warnings[1]
    assert warning2.txn == txn_2
    assert warning2.msg == "I warned you!"
    assert warning2.state.last_txn == txn_2    
    StubTransaction.check(warning2.state, txn_1)

# TODO: Test logging
