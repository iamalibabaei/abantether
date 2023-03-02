from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from .exceptions import NotEnoughMoneyException


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    credit = models.DecimalField(max_digits=25, decimal_places=4, default=0)
    blocked_credit = models.DecimalField(max_digits=25, decimal_places=4, default=0)

    def _can_purchase(self, amount: Decimal):
        return self.credit >= amount

    def purchase(self, amount: Decimal):
        if not self._can_purchase(amount):
            raise NotEnoughMoneyException()
        self.credit -= amount
        self.blocked_credit += amount

    def finalize_purchase(self, amount: Decimal):
        self.blocked_credit -= amount

    def rollback_purchase(self, amount: Decimal):
        self.blocked_credit -= amount
        self.credit += amount

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class CryptoCurrency(models.Model):
    name = models.CharField(max_length=200, unique=True, db_index=True)
    price = models.DecimalField(max_digits=15, decimal_places=4)

    def __str__(self):
        return self.name


class Transaction(models.Model):
    CREATED = "CREATED"
    IN_PROGRESS = "IN_PROGRESS"
    REQUEST_SENT = "REQUEST_SENT"
    FINALIZED = "FINALIZED"
    FAILED = "FAILED"
    STATUS_CHOICES = [
        (CREATED, "created"),
        (IN_PROGRESS, "in_progress"),
        (REQUEST_SENT, "request_sent"),
        (FINALIZED, "finalized"),
        (FAILED, "failed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    currency = models.ForeignKey(CryptoCurrency, on_delete=models.CASCADE)

    amount = models.DecimalField(max_digits=15, decimal_places=4)
    price = models.DecimalField(max_digits=25, decimal_places=4)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.first_name}: {self.currency.name} - {self.amount}"


@receiver(post_save, sender=User)
def create_user_account(sender, instance, created, **kwargs):
    if created:
        Account.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_account(sender, instance, **kwargs):
    instance.account.save()
