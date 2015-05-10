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
            txn_datetime=datetime.datetime(2015,5,9))

        self.table_state = self.table.process()

    def test_authorize_txn(self):
        """Table should have an authorize transaction"""        
        self.assertEqual(len(self.table.transactions), 1)

        transaction = self.table.transactions[0]
        assert isinstance(transaction, captable.AuthTransaction)


    def test_authorize_amount(self):
        """Table should have list outstanding amounts for each class
        """
        classACommon = self.table_state.get_amounts("Class A Common Stock")
        self.assertEqual(classACommon.authorized, 1000000)
        self.assertEqual(classACommon.issued, 0)
        self.assertEqual(classACommon.outstanding, 0)
        self.assertEqual(classACommon.reserved, 0)

        classBCommon = self.table_state.get_amounts("Class B Common Stock")
        self.assertEqual(classBCommon.authorized, 500000)
        self.assertEqual(classACommon.issued, 0)
        self.assertEqual(classBCommon.outstanding, 0)
        self.assertEqual(classBCommon.reserved, 0)
