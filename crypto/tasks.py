from decimal import Decimal
from typing import List

from celery import shared_task
from django.db import transaction as db_transaction
from django.db.models import Sum, Subquery

from .exchange.exchange import MyExchange
from .models import Transaction, Account

exchange = MyExchange()


@shared_task(
    name="finalize_transaction",
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 10, "countdown": 5},
)
def finalize_transaction(transaction_id: int, success: bool):
    with db_transaction.atomic():
        transaction = (
            Transaction.objects.filter(pk=transaction_id, status=Transaction.REQUEST_SENT)
            .select_for_update(skip_locked=True)
            .first()
        )
        if success:
            account = (
                Account.objects.filter(user=transaction.user)
                .select_for_update()
                .first()
            )
            transaction.status = Transaction.FINALIZED
            account.finalize_purchase(transaction.price)
            transaction.save()
            account.save()
        else:
            account = (
                Account.objects.filter(user=transaction.user)
                .select_for_update()
                .first()
            )
            transaction.status = Transaction.FAILED
            account.rollback_purchase(transaction.price)
            transaction.save()
            account.save()


@shared_task(name="buy_crypto")
def buy_crypto(transaction_id: int):
    with db_transaction.atomic():
        transaction = (
            Transaction.objects.filter(pk=transaction_id, status=Transaction.IN_PROGRESS)
            .select_for_update(skip_locked=True)
            .first()
        )
        done = exchange.buy_from_exchange(transaction.currency.name, transaction.price)
        transaction.status = Transaction.REQUEST_SENT
        transaction.save()
        if done:
            finalize_transaction.delay(transaction_id, True)
        else:
            finalize_transaction.delay(transaction_id, False)


@shared_task(name="buy_crypto_bulk")
def buy_crypto_bulk(transaction_ids: List[int], name: str, price: Decimal):
    with db_transaction.atomic():
        transactions = Transaction.objects.filter(
            pk__in=transaction_ids, status=Transaction.IN_PROGRESS
        ).select_for_update(skip_locked=True)

        done = exchange.buy_from_exchange(name, price)
        for transaction in transactions:
            transaction.status = Transaction.REQUEST_SENT
            transaction.save()

        if done:
            for transaction in transactions:
                finalize_transaction.delay(transaction.pk, True)
        else:
            for transaction in transactions:
                finalize_transaction.delay(transaction.pk, False)


@shared_task(name="finalize_transactions_more_than_ten_dollars")
def finalize_transactions_more_than_ten_dollars():
    with db_transaction.atomic():
        transactions = Transaction.objects.filter(
            status=Transaction.CREATED,
            price__gte=10,
        ).select_for_update(skip_locked=True)

        for transaction in transactions:
            transaction.status = Transaction.IN_PROGRESS
            transaction.save()
            buy_crypto.delay(transaction.pk)


@shared_task(name="finalize_transactions_less_than_ten_dollars")
def finalize_transactions_less_than_ten_dollars():
    with db_transaction.atomic():
        transactions = Transaction.objects.filter(
            status=Transaction.CREATED,
            price__lt=10,
            currency__in=Subquery(
                Transaction.objects.filter(
                    status=Transaction.CREATED,
                    price__lt=10,
                )
                .values("currency")
                .annotate(total_price=Sum("price"))
                .filter(total_price__gte=10)
                .values("currency")
            ),
        ).select_for_update()

        transaction_groups: dict = {}
        for transaction in transactions:
            tmp = transaction_groups.get(transaction.currency.name, [])
            tmp.append(transaction)
            transaction_groups[transaction.currency.name] = tmp

        for transaction in transaction_groups.keys():
            for t in transaction_groups[transaction]:
                t.status = Transaction.IN_PROGRESS
                t.save()
            buy_crypto_bulk.delay(
                list(map(lambda x: x.pk, transaction_groups[transaction])),
                transaction,
                sum(map(lambda x: x.price, transaction_groups[transaction])),
            )
