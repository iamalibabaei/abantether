from rest_framework.exceptions import APIException


class NotEnoughMoneyException(APIException):
    status_code = 422
    default_detail = "You do not have enough credit to purchase"
    default_code = "not_enough_money"
