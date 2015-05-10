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

        self.classACommon = ClassACommon
        self.classBCommon = ClassBCommon

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

        #TODO: Test time


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


class MultipleAuthTests(AuthTests):
    def setUp(self):
        """Change number of shares of stock"""
        super(MultipleAuthTests, self).setUp()
        self.table.authorize(
            classes=[{
                "cls": self.classBCommon,
                "amount": 750000
            }],
            txn_datetime=datetime.datetime(2015,5,10))
        self.table_state = self.table.process()

    def test_authorize_txn(self):
        """Table should have a new authorize transaction"""        
        self.assertEqual(len(self.table.transactions), 2)

        transaction = self.table.transactions[1]
        assert isinstance(transaction, captable.AuthTransaction)

    def test_authorize_amount(self):
        """Old classes should be unchanged -- specified class should have new
        updated numbers"""
        classACommon = self.table_state.get_amounts("Class A Common Stock")
        self.assertEqual(classACommon.authorized, 1000000)
        self.assertEqual(classACommon.issued, 0)
        self.assertEqual(classACommon.outstanding, 0)
        self.assertEqual(classACommon.reserved, 0)

        classBCommon = self.table_state.get_amounts("Class B Common Stock")
        self.assertEqual(classBCommon.authorized, 750000)
        self.assertEqual(classACommon.issued, 0)
        self.assertEqual(classBCommon.outstanding, 0)
        self.assertEqual(classBCommon.reserved, 0)


class DeltaAuthTests(AuthTests):
    def setUp(self):
        """Authorize a delta change to the number of shares of stock"""
        super(DeltaAuthTests, self).setUp()
        self.table.authorize(
            classes=[{
                "cls": self.classBCommon,
                "delta": 250000
            }],
            txn_datetime=datetime.datetime(2015,5,10))
        self.table_state = self.table.process()

    def test_authorize_txn(self):
        """Table should have a new authorize transaction"""        
        self.assertEqual(len(self.table.transactions), 2)

        transaction = self.table.transactions[1]
        assert isinstance(transaction, captable.AuthTransaction)

    def test_authorize_amount(self):
        """Old classes should be unchanged -- specified class should have new
        updated numbers"""
        classACommon = self.table_state.get_amounts("Class A Common Stock")
        self.assertEqual(classACommon.authorized, 1000000)
        self.assertEqual(classACommon.issued, 0)
        self.assertEqual(classACommon.outstanding, 0)
        self.assertEqual(classACommon.reserved, 0)

        classBCommon = self.table_state.get_amounts("Class B Common Stock")
        self.assertEqual(classBCommon.authorized, 750000)
        self.assertEqual(classACommon.issued, 0)
        self.assertEqual(classBCommon.outstanding, 0)
        self.assertEqual(classBCommon.reserved, 0)