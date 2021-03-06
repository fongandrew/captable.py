from __future__ import absolute_import

import captable
import datetime
import pytest
from ._helpers import StubTransaction


def test_custom_validators():
    "Test that custom validators work when processing transactions"
    def max_2_stubs(state):
        assert StubTransaction.count(state) <= 2, "Too many stubs"

    table = captable.CapTable(validators=[max_2_stubs])

    txn_1 = StubTransaction()
    txn_2 = StubTransaction()
    txn_3 = StubTransaction()

    table.record(datetime.datetime(2015, 5, 1), txn_1)
    table.record(datetime.datetime(2015, 5, 2), txn_2)

    with pytest.raises(AssertionError):
        table.record(datetime.datetime(2015, 5, 3), txn_3)

    # Check that last tranaction was not recorded
    assert table.transactions == [
        (datetime.datetime(2015, 5, 1), txn_1),
        (datetime.datetime(2015, 5, 2), txn_2)
    ]

    # Check that last transaction did not modify state
    StubTransaction.check(table.state, txn_1, txn_2)


def test_amount_validator():
    "Test the default check_auth validator"
    table = captable.CapTable()
    table.record(None, captable.CommonStock.auth(1000))

    # Test transaction function that changes the "issued" amount to 2000
    # and should trigger the check_auth validator
    class TestStock(captable.CommonStock):
        class MetaState(captable.CommonStock.MetaState):
            issued = 2000

    with pytest.raises(AssertionError):
        table.record(None, TestStock.auth())
