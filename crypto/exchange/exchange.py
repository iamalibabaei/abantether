from abc import ABC, abstractmethod
from decimal import Decimal


class ExchangeService(ABC):
    @abstractmethod
    def buy_from_exchange(self, currency: str, price: Decimal) -> bool:
        pass


class MyExchange(ExchangeService):
    def buy_from_exchange(self, currency: str, price: Decimal) -> bool:
        # implementation goes here
        return True
