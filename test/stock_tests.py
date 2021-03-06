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

def test_issuance_by_cert_no():
    """Issuing stock with a cert_no should allow us to identify specific
    issuances by that cert_no and that certain attributes are set on the
    certificate.
    """
    pg = Person("Peter Gregory")
    gb = Person("Gavin Belson")

    table = CapTable()
    table.record(None, CommonStock.auth(5000))
    table.record(None, CommonStock.issue(holder=pg, 
                                         amount=1000, cert_no="CS-1"))
    table.record(None, CommonStock.issue(holder=gb, 
                                         amount=2000, cert_no="CS-2"))

    cs1 = table[CommonStock]["CS-1"]
    assert cs1.cert_no == "CS-1"
    assert cs1.holder == pg
    assert cs1.amount == 1000
    assert cs1.cert_name == "Peter Gregory"
    assert not cs1.cancelled 

    cs2 = table[CommonStock]["CS-2"]
    assert cs2.cert_no == "CS-2"
    assert cs2.holder == gb
    assert cs2.amount == 2000
    assert cs2.cert_name == "Gavin Belson"
    assert not cs2.cancelled

def test_non_unique_cert_no():
    """Should not be able to re-use a cert_no while it is still in use
    """
    pg = Person("Peter Gregory")
    gb = Person("Gavin Belson")

    table = CapTable()
    table.record(None, CommonStock.auth(5000))
    table.record(None, CommonStock.issue(holder=pg, 
                                         amount=1000, cert_no="CS-1"))
    with pytest.raises(ValueError):
        table.record(None, CommonStock.issue(holder=pg, 
                                             amount=2000, cert_no="CS-1"))

def test_transfer_cert():
    """Should be able to transfer a particular stock certificate from one
    holder to another. This is used to note that the actual certificate has 
    been handed off from one party to another, but that the name on the 
    certificate (or in the books) has not necessarily changed.
    """
    pg = Person("Peter Gregory")
    gb = Person("Gavin Belson")

    table = CapTable()
    table.record(None, CommonStock.auth(5000))
    table.record(None, CommonStock.issue(holder=pg, 
                                         amount=1000, cert_no="CS-1"))
    table.record(None, CommonStock.transfer(cert_no="CS-1", to=gb))

    cs1 = table[CommonStock]["CS-1"]
    assert cs1.cert_no == "CS-1"
    assert cs1.holder == gb
    assert cs1.amount == 1000
    assert cs1.cert_name == "Peter Gregory" # This does not change because
                                            # we need to cancel and re-issue
                                            # a new certificate to change name
    assert not cs1.cancelled

def test_treasury_stock():
    """Should be able to reclaim stock as treasury shares"""
    pg = Person("Peter Gregory")

    table = CapTable()
    table.record(None, CommonStock.auth(5000))
    table.record(None, CommonStock.issue(holder=pg, 
                                         amount=1000, cert_no="CS-1"))
    table.record(None, CommonStock.transfer(cert_no="CS-1", to=None))

    # Holder updated but certificate is not necessarily cancelled
    cs1 = table[CommonStock]["CS-1"]
    assert cs1.holder == None
    assert not cs1.cancelled

    # Oustanding number should be updated though
    metastate = table[CommonStock]
    assert metastate.issued == 1000
    assert metastate.outstanding == 0

    # Treasury stock should be re-issuable.
    assert metastate.issuable == 5000

def test_cancel():
    """Should be able to cancel an old certificate"""
    pg = Person("Peter Gregory")
    gb = Person("Gavin Belson")

    table = CapTable()
    table.record(None, CommonStock.auth(5000))
    table.record(None, CommonStock.issue(holder=pg, 
                                         amount=1000, cert_no="CS-1"))
    table.record(None, CommonStock.issue(holder=gb, 
                                         amount=2000, cert_no="CS-2"))

    table.record(None, CommonStock.cancel(cert_no="CS-1"))

    # CS-1 is still accessible but should show up as canceled
    cs1 = table[CommonStock]["CS-1"]
    assert cs1.cert_no == "CS-1"
    assert cs1.holder == pg
    assert cs1.amount == 1000
    assert cs1.cert_name == "Peter Gregory"
    assert cs1.cancelled

    # Issued / outsanding numbers should change
    metastate = table[CommonStock]
    assert metastate.issued == 2000
    assert metastate.outstanding == 2000
    assert metastate.issuable == 3000

def test_retire_stock_reissuable():
    """Test that retiring stock works allows for stock to be re-issuable again
    by default"""
    pg = Person("Peter Gregory")

    table = CapTable()
    table.record(None, CommonStock.auth(5000))
    table.record(None, CommonStock.issue(holder=pg, 
                                         amount=1000, cert_no="CS-1"))

    # Retire stock
    table.record(None, CommonStock.retire('CS-1'))
    cs1 = table[CommonStock]["CS-1"]
    assert cs1.cancelled

    # Still authorized
    metastate = table[CommonStock]
    assert metastate.authorized == 5000
    assert metastate.issued == 0
    assert metastate.outstanding == 0
    assert metastate.issuable == 5000

def test_retire_stock_deauth():
    """Test that we can set up a class of stock that deauthorizes retired
    shares of stock
    """
    pg = Person("Peter Gregory")

    table = CapTable()
    table.record(None, CommonStock.auth(5000))
    table.record(None, CommonStock.issue(holder=pg, 
                                         amount=1000, cert_no="CS-1"))

    # Amend common stock to disallow reissue of retired stock
    class CommonStock2(CommonStock):
        class MetaState(CommonStock.MetaState):
            DEAUTH_RETIRED = True
    table.record(None, CommonStock2.auth())

    # Retire stock
    table.record(None, CommonStock2.retire('CS-1'))
    cs1 = table[CommonStock2]["CS-1"]
    assert cs1.cancelled

    # Deauthorized retired shares
    metastate = table[CommonStock2]
    assert metastate.authorized == 4000
    assert metastate.issued == 0
    assert metastate.outstanding == 0
    assert metastate.issuable == 4000
