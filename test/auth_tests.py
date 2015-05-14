from __future__ import absolute_import

import captable
import unittest
import datetime


CLASS_A_COMMON = captable.CommonStock("Class A Common Stock")
CLASS_B_COMMON = captable.CommonStock("Class B Common Stock")

class AuthTests(unittest.TestCase):
    """Test authorization of classes of securities"""

    def setUp(self):
        """Initialize a blank captable and authorize multiple classes of
        securities"""
        self.table = captable.CapTable()
        self.table.record_multi_txn(txns=[
            captable.AuthTransaction(security=CLASS_A_COMMON, amount=1000000),
            captable.AuthTransaction(security=CLASS_B_COMMON, amount=500000),
        ], txn_datetime=datetime.datetime(2015,5,9))
        self.table_state = self.table.process()
    
    def test_authorize_amount(self):
        """Table should have list outstanding amounts for each class
        """
        amountsA = self.table_state.get_security_state(CLASS_A_COMMON)
        self.assertEqual(amountsA.authorized, 1000000)
        self.assertEqual(amountsA.issuable, 1000000)
        self.assertEqual(amountsA.unreserved, 1000000)
        self.assertEqual(amountsA.outstanding, 0)

        amountsB = self.table_state.get_security_state(CLASS_B_COMMON)
        self.assertEqual(amountsB.authorized, 500000)
        self.assertEqual(amountsB.issuable, 500000)
        self.assertEqual(amountsB.unreserved, 500000)
        self.assertEqual(amountsB.outstanding, 0)


# class MultipleAuthTests(AuthTests):
#     def setUp(self):
#         """Change number of shares of stock"""
#         super(MultipleAuthTests, self).setUp()
#         self.table.record_txn(
#             captable.AuthTransaction(
#                 cls=ClassBCommon,
#                 amount=750000,
#                 txn_datetime=datetime.datetime(2015,5,10)))
#         self.table_state = self.table.process()

#     def test_authorize_amount(self):
#         """Old classes should be unchanged -- specified class should have new
#         updated numbers"""
#         amountsA = self.table_state.get_amounts(ClassACommon)
#         self.assertEqual(amountsA.authorized, 1000000)
#         self.assertEqual(amountsA.issued, 0)
#         self.assertEqual(amountsA.outstanding, 0)
#         self.assertEqual(amountsA.reserved, 0)

#         amountsB = self.table_state.get_amounts(ClassBCommon)
#         self.assertEqual(amountsB.authorized, 750000)
#         self.assertEqual(amountsB.issued, 0)
#         self.assertEqual(amountsB.outstanding, 0)
#         self.assertEqual(amountsB.reserved, 0)

# class DeltaAuthTests(AuthTests):
#     def setUp(self):
#         """Authorize a delta change to the number of shares of stock"""
#         super(DeltaAuthTests, self).setUp()
#         self.table.record_txn(
#             captable.AuthTransaction(
#                 cls=ClassBCommon,
#                 delta=250000,
#                 txn_datetime=datetime.datetime(2015,5,10)))
#         self.table_state = self.table.process()

#     def test_authorize_amount(self):
#         """Old classes should be unchanged -- specified class should have new
#         updated numbers"""
#         amountsA = self.table_state.get_amounts(ClassACommon)
#         self.assertEqual(amountsA.authorized, 1000000)
#         self.assertEqual(amountsA.issued, 0)
#         self.assertEqual(amountsA.outstanding, 0)
#         self.assertEqual(amountsA.reserved, 0)

#         amountsB = self.table_state.get_amounts(ClassBCommon)
#         self.assertEqual(amountsB.authorized, 750000)
#         self.assertEqual(amountsB.issued, 0)
#         self.assertEqual(amountsB.outstanding, 0)
#         self.assertEqual(amountsB.reserved, 0)

# amount / delta - error check