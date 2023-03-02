from django.contrib.auth.models import User

import unittest

from crypto import exceptions


class TestAccount(unittest.TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(username="username", password="1234")
        self.user.account.credit = 20
        self.user.account.save()

    def tearDown(self) -> None:
        self.user.account.delete()
        self.user.delete()

    def test_purchase(self):
        self.user.account.purchase(15)
        self.user.account.save()

        self.assertEqual(self.user.account.credit, 5)
        self.assertEqual(self.user.account.blocked_credit, 15)

    def test_purchase_more_than_credit(self):
        with self.assertRaises(exceptions.NotEnoughMoneyException):
            self.user.account.purchase(25)

        self.assertEqual(self.user.account.credit, 20)
        self.assertEqual(self.user.account.blocked_credit, 0)

    def test_finalize_purchase(self):
        self.user.account.purchase(15)
        self.user.account.save()

        self.assertEqual(self.user.account.credit, 5)
        self.assertEqual(self.user.account.blocked_credit, 15)

        self.user.account.finalize_purchase(15)

        self.assertEqual(self.user.account.credit, 5)
        self.assertEqual(self.user.account.blocked_credit, 0)

    def test_rollback_purchase(self):
        self.user.account.purchase(15)
        self.user.account.save()

        self.assertEqual(self.user.account.credit, 5)
        self.assertEqual(self.user.account.blocked_credit, 15)

        self.user.account.rollback_purchase(15)

        self.assertEqual(self.user.account.credit, 20)
        self.assertEqual(self.user.account.blocked_credit, 0)
