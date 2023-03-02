from rest_framework import serializers

from ..models import CryptoCurrency


class PurchaseSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    amount = serializers.DecimalField(max_digits=25, decimal_places=4)

    def validate_name(self, name):
        if not CryptoCurrency.objects.filter(name=name).exists():
            raise serializers.ValidationError("The currency does not exists")
        return name
