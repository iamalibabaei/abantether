from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import PurchaseSerializer
from ..models import CryptoCurrency, Transaction, Account


# This view is just for the need of this project. ignore it :))
@login_required
def increase_credit(request):
    user = request.user
    user.account.credit += 1000
    user.account.save()

    return Response({"status": "success"})


class PurchaseCurrencyViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class_by_action = {
        "purchase": PurchaseSerializer,
    }

    def get_serializer_class(self):
        if self.action not in self.serializer_class_by_action:
            raise Exception
        return self.serializer_class_by_action[self.action]

    @action(detail=False, methods=["post"])
    def purchase(self, request):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        account = Account.objects.filter(user=request.user).select_for_update().first()
        currency = get_object_or_404(
            CryptoCurrency, name=serializer.validated_data["name"]
        )
        price = currency.price * serializer.validated_data["amount"]
        account.purchase(price)
        account.save()
        Transaction.objects.create(
            user=request.user,
            currency=currency,
            amount=serializer.validated_data["amount"],
            price=price,
            status=Transaction.CREATED,
        )
        return Response({"status": "success"}, status=status.HTTP_200_OK)
