import unittest
from decimal import Decimal
from unittest.mock import patch, call

from django.contrib.auth.models import User

from ..models import Transaction, CryptoCurrency, Account
from ..tasks import (
    finalize_transactions_more_than_ten_dollars,
    finalize_transactions_less_than_ten_dollars,
    buy_crypto,
    buy_crypto_bulk,
    finalize_transaction,
)


class TestTasks(unittest.TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(username="username", password="1234")
        self.user.account.credit = 100
        self.user.account.blocked_credit = 100
        self.user.account.save()
        self.busd = CryptoCurrency.objects.create(name="BUSD", price=1)

    def tearDown(self) -> None:
        User.objects.all().delete()
        CryptoCurrency.objects.all().delete()
        Transaction.objects.all().delete()

    @patch("crypto.tasks.buy_crypto.delay")
    def test_finalize_transactions_more_than_ten_dollars(self, buy_crypto):
        transaction = Transaction.objects.create(
            user=self.user,
            currency=self.busd,
            amount=15,
            price=15,
            status=Transaction.CREATED,
        )
        finalize_transactions_more_than_ten_dollars()
        new_transaction = Transaction.objects.get(pk=transaction.pk)
        self.assertEqual(new_transaction.status, Transaction.IN_PROGRESS)
        buy_crypto.assert_called_with(transaction.pk)

    @patch("crypto.tasks.buy_crypto_bulk.delay")
    def test_finalize_transactions_less_than_ten_dollars(self, buy_crypto_bulk):
        transaction_one = Transaction.objects.create(
            user=self.user,
            currency=self.busd,
            amount=7,
            price=7,
            status=Transaction.CREATED,
        )
        transaction_two = Transaction.objects.create(
            user=self.user,
            currency=self.busd,
            amount=7,
            price=7,
            status=Transaction.CREATED,
        )
        finalize_transactions_less_than_ten_dollars()
        new_transaction_one = Transaction.objects.get(pk=transaction_one.pk)
        self.assertEqual(new_transaction_one.status, Transaction.IN_PROGRESS)
        new_transaction_two = Transaction.objects.get(pk=transaction_two.pk)
        self.assertEqual(new_transaction_two.status, Transaction.IN_PROGRESS)
        buy_crypto_bulk.assert_called_with(
            [transaction_one.pk, transaction_two.pk], self.busd.name, Decimal(14.0000)
        )

    @patch("crypto.tasks.finalize_transaction.delay")
    def test_buy_crypto(self, finalize_transaction_mock):
        transaction = Transaction.objects.create(
            user=self.user,
            currency=self.busd,
            amount=15,
            price=15,
            status=Transaction.IN_PROGRESS,
        )
        buy_crypto(transaction.pk)
        new_transaction = Transaction.objects.get(pk=transaction.pk)
        self.assertEqual(new_transaction.status, Transaction.REQUEST_SENT)
        finalize_transaction_mock.assert_called_with(transaction.pk, True)

    @patch("crypto.tasks.finalize_transaction.delay")
    def test_buy_crypto_bulk(self, finalize_transaction_mock):
        transaction_one = Transaction.objects.create(
            user=self.user,
            currency=self.busd,
            amount=7,
            price=7,
            status=Transaction.IN_PROGRESS,
        )
        transaction_two = Transaction.objects.create(
            user=self.user,
            currency=self.busd,
            amount=7,
            price=7,
            status=Transaction.IN_PROGRESS,
        )
        buy_crypto_bulk(
            [transaction_one.pk, transaction_two.pk], self.busd.name, Decimal(14)
        )
        new_transaction_one = Transaction.objects.get(pk=transaction_one.pk)
        self.assertEqual(new_transaction_one.status, Transaction.REQUEST_SENT)
        new_transaction_two = Transaction.objects.get(pk=transaction_two.pk)
        self.assertEqual(new_transaction_two.status, Transaction.REQUEST_SENT)
        self.assertEqual(finalize_transaction_mock.call_count, 2)
        finalize_transaction_mock.assert_has_calls(
            [
                call(transaction_one.pk, True),
                call(transaction_two.pk, True),
            ]
        )

    def test_finalize_transaction_success(self):
        transaction = Transaction.objects.create(
            user=self.user,
            currency=self.busd,
            amount=7,
            price=7,
            status=Transaction.REQUEST_SENT,
        )
        finalize_transaction(transaction.pk, True)
        account = Account.objects.get(user=self.user)
        self.assertEqual(account.blocked_credit, 93)
        self.assertEqual(account.credit, 100)
        new_transaction = Transaction.objects.get(pk=transaction.pk)
        self.assertEqual(new_transaction.status, Transaction.FINALIZED)

    def test_finalize_transaction_failed(self):
        transaction = Transaction.objects.create(
            user=self.user,
            currency=self.busd,
            amount=7,
            price=7,
            status=Transaction.REQUEST_SENT,
        )
        finalize_transaction(transaction.pk, False)
        account = Account.objects.get(user=self.user)
        self.assertEqual(account.blocked_credit, 93)
        self.assertEqual(account.credit, 107)
        new_transaction = Transaction.objects.get(pk=transaction.pk)
        self.assertEqual(new_transaction.status, Transaction.FAILED)
