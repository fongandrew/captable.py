from __future__ import absolute_import

import datetime
import pytest

from captable import CapTable, CommonStock, Person


def test_auth_before_issue():
    """Should not be able to issue stock before authorizing it"""
    # Disable validators so we can test transaction is at work, not validators
    table = CapTable(validators=[])
    holder = Person("Peter Gregory")
    with pytest.raises(RuntimeError):
        table.record(None, CommonStock.issue(holder=holder, amount=1000))

def test_excess_auth():
    """Should not be able to issue stock in excess of authorization"""
    # Disable validators so we can test transaction is at work, not validators
    table = CapTable(validators=[])
    pg = Person("Peter Gregory")
    gb = Person("Gavin Belson")
    table.record(None, CommonStock.auth(1000))
    table.record(None, CommonStock.issue(holder=pg, amount=500))
    with pytest.raises(AssertionError):
        table.record(None, CommonStock.issue(holder=gb, amount=501))

def test_issuance_outstanding_amounts():
    """Issuing stock should update issued, outstanding, and issuable numbers
    accordingly"""
    pg = Person("Peter Gregory")
    gb = Person("Gavin Belson")

    table = CapTable()
    table.record(None, CommonStock.auth(5000))
    table.record(None, CommonStock.issue(holder=pg, amount=1000))
    table.record(None, CommonStock.issue(holder=gb, amount=2000))

    assert table[CommonStock].issued == 3000
    assert table[CommonStock].outstanding == 3000
    assert table[CommonStock].issuable == 2000

