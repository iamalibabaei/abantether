from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from crypto.models import CryptoCurrency, Transaction, Account


class TransactionTest(APITestCase):
    """Test Transaction API"""

    def setUp(self):
        self.user = User.objects.create(username="username", password="1234")
        self.user.account.credit = 20
        self.user.account.save()
        self.usdt = CryptoCurrency.objects.create(
            name="USDT",
            price=1,
        )

    def test_create_transaction(self):
        self.client.force_login(self.user)
        data = {"name": self.usdt.name, "amount": 15}
        response = self.client.post(reverse("purchase"), data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, Transaction.objects.count())
        transaction = Transaction.objects.first()
        self.assertEqual(transaction.status, Transaction.CREATED)
        self.assertEqual(transaction.currency, self.usdt)
        self.assertEqual(transaction.user, self.user)
        self.assertEqual(transaction.amount, 15)
        self.assertEqual(transaction.price, 15)
        account = Account.objects.filter(user=self.user).first()
        self.assertEqual(account.credit, 5)
        self.assertEqual(account.blocked_credit, 15)

    def test_not_enough_money(self):
        self.client.force_login(self.user)
        data = {"name": self.usdt.name, "amount": 100}
        response = self.client.post(reverse("purchase"), data=data)
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(0, Transaction.objects.count())
