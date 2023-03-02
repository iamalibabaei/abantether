from django.urls import path

from .api.views import increase_credit, PurchaseCurrencyViewSet


purchase = PurchaseCurrencyViewSet.as_view({"post": "purchase"})

urlpatterns = [
    path("increase/", increase_credit),
    path("purchase/", purchase, name="purchase"),
]
