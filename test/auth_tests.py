from __future__ import absolute_import

import captable
import unittest
import datetime
import pytest


CLASS_A_COMMON = captable.CommonStock("Class A Common Stock")
CLASS_B_COMMON = captable.CommonStock("Class B Common Stock")

class AuthTests(unittest.TestCase):
    """Test authorization of classes of securities"""

    def setUp(self):
        """Initialize a blank captable and authorize multiple classes of
        securities"""
        self.table = captable.CapTable()
        self.table.record_multi(datetime.datetime(2015,5,9),
            captable.AuthTransaction(security=CLASS_A_COMMON, amount=1000000),
            captable.AuthTransaction(security=CLASS_B_COMMON, amount=500000))

    def checkAuth(self, security, total):
        amounts = self.table.state[security]
        self.assertEqual(amounts.authorized, total)
        self.assertEqual(amounts.issuable, total)
        self.assertEqual(amounts.unreserved, total)
        self.assertEqual(amounts.outstanding, 0)
    
    def test_authorize_amount(self):
        """Table should have list outstanding amounts for each class
        """
        self.checkAuth(CLASS_A_COMMON, 1000000)
        self.checkAuth(CLASS_B_COMMON, 500000)


class MultipleAuthTests(AuthTests):
    def setUp(self):
        """Change number of shares of stock"""
        super(MultipleAuthTests, self).setUp()
        self.table.record(datetime.datetime(2015,5,10),
            captable.AuthTransaction(security=CLASS_B_COMMON, amount=750000))

    def test_authorize_amount(self):
        """Old classes should be unchanged -- specified class should have new
        updated numbers"""
        self.checkAuth(CLASS_A_COMMON, 1000000)
        self.checkAuth(CLASS_B_COMMON, 750000)


class DeltaAuthTests(MultipleAuthTests):
    def setUp(self):
        """Authorize a delta change to the number of shares of stock"""
        super(MultipleAuthTests, self).setUp()
        self.table.record(datetime.datetime(2015,5,10),
            captable.AuthTransaction(security=CLASS_B_COMMON, delta=250000))


class DeltaPlusAmountAuthTests(MultipleAuthTests):
    def setUp(self):
        """Authorize a delta change to the number of shares of stock along
        with a conforming amount"""
        super(MultipleAuthTests, self).setUp()
        self.table.record(datetime.datetime(2015,5,10),
            captable.AuthTransaction(security=CLASS_B_COMMON,
                                     delta=250000,
                                     amount=750000))


def test_delta_amount_mismatch():
    """Mismatch between delta number and amount number should raise an
    AssertionError"""
    table = captable.CapTable()
    table.record(datetime.datetime(2015,5,9),
        captable.AuthTransaction(security=CLASS_A_COMMON, amount=500000))
    with pytest.raises(AssertionError):
        table.record(datetime.datetime(2015,5,10),
            captable.AuthTransaction(security=CLASS_A_COMMON,
                                     amount=1000000, delta=250000))
