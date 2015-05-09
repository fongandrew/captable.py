from __future__ import absolute_import

import captable
import unittest
import datetime

class AuthTests(unittest.TestCase):
    """Test authorization of classes of securities"""

    def setUp(self):
        """Initialize a blank captable and authorize multiple classes of
        securities"""
        class ClassACommon(captable.CommonStock):
            name = "Class A Common Stock"

        class ClassBCommon(captable.CommonStock):
            name = "Class B Common Stock"

        self.table = captable.CapTable()
        self.table.authorize(
            classes=[{
                "cls": ClassACommon,
                "amount": 1000000
            }, {
                "cls": ClassBCommon,
                "amount": 500000
            }],
            date=datetime.datetime(2015,5,9))

    def test_authorize_txn(self):
        """Table should have an authorize transaction"""        
        self.assertEqual(len(self.table.transactions), 1)

        transaction = self.table.transactions[0]
        assert isinstance(transaction, captable.AuthTransaction)
