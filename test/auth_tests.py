from __future__ import absolute_import

import captable
import unittest
import datetime
import pytest


class ClassACommon(captable.CommonStock):
    name = "Class A Common Stock"

class ClassBCommon(captable.CommonStock):
    name = "Class B Common Stock"


class AuthTests(unittest.TestCase):
    """Test authorization of classes of securities"""

    def setUp(self):
        """Initialize a blank captable and authorize multiple classes of
        securities"""
        self.table = captable.CapTable()
        self.table.record_multi(datetime.datetime(2015,5,9),
                                ClassACommon.auth(1000000),
                                ClassBCommon.auth(500000))

    def check_auth(self, security, total):
        amounts = self.table[security]
        self.assertEqual(amounts.authorized, total)
        self.assertEqual(amounts.issuable, total)
        self.assertEqual(amounts.unreserved, total)
        self.assertEqual(amounts.outstanding, 0)
    
    def test_authorize_amount(self):
        """Table should have list outstanding amounts for each class
        """
        self.check_auth(ClassACommon, 1000000)
        self.check_auth(ClassBCommon, 500000)


class MultipleAuthTests(AuthTests):
    def setUp(self):
        """Change number of shares of stock"""
        super(MultipleAuthTests, self).setUp()
        self.table.record(datetime.datetime(2015,5,10),
                          ClassBCommon.auth(750000))

    def test_authorize_amount(self):
        """Old classes should be unchanged -- specified class should have new
        updated numbers"""
        self.check_auth(ClassACommon, 1000000)
        self.check_auth(ClassBCommon, 750000)


class DeltaAuthTests(MultipleAuthTests):
    def setUp(self):
        """Authorize a delta change to the number of shares of stock"""
        super(MultipleAuthTests, self).setUp()
        self.table.record(datetime.datetime(2015,5,10),
                          ClassBCommon.auth(delta=250000))


class DeltaPlusAmountAuthTests(MultipleAuthTests):
    def setUp(self):
        """Authorize a delta change to the number of shares of stock along
        with a conforming amount"""
        super(MultipleAuthTests, self).setUp()
        self.table.record(datetime.datetime(2015,5,10),
                          ClassBCommon.auth(delta=250000, amount=750000))


def test_delta_amount_mismatch():
    """Mismatch between delta number and amount number should raise an
    AssertionError"""
    table = captable.CapTable()
    table.record(datetime.datetime(2015,5,9), ClassACommon.auth(500000))
    with pytest.raises(AssertionError):
        table.record(datetime.datetime(2015,5,10),
                     ClassACommon.auth(delta=250000, amount=1000000))


def test_update_metastate():
    """If the name of two classes of stock is the same, then authorizing one,
    then the other, should result in the latter's MetaState object replacing
    the former
    """
    table = captable.CapTable()
    table.record(datetime.datetime(2015,5,9), 
                 captable.CommonStock.auth(500000))

    metastate = table[captable.CommonStock]
    assert metastate.__class__ == captable.CommonStock.MetaState

    metastate.prop = 123

    class CommonStock2(captable.CommonStock):
        class MetaState(captable.CommonStock.MetaState):
            pass
    table.record(None, CommonStock2.auth())

    # Class updated
    metastate = table[captable.CommonStock]
    assert metastate.__class__ == CommonStock2.MetaState
    assert metastate.__class__ != captable.CommonStock.MetaState # Sanity check

    # Properties preserved
    assert metastate.prop == 123
    assert metastate.authorized == 500000







