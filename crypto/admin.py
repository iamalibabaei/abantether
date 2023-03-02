from django.contrib import admin

from .models import Account, CryptoCurrency, Transaction


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("__str__", "first_name", "last_name", "user", "credit")
    sortable_by = (
        "__str__",
        "user",
        "credit",
    )

    @admin.display(ordering="user__first_name")
    def first_name(self, obj):
        return obj.user.first_name

    @admin.display(ordering="user__last_name")
    def last_name(self, obj):
        return obj.user.last_name


@admin.register(CryptoCurrency)
class CryptoCurrencyAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "price",
    )
    sortable_by = (
        "__str__",
        "price",
    )


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "status",
    )
    sortable_by = (
        "__str__",
        "status",
    )
