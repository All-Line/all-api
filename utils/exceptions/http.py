from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import APIException


class HttpPaymentRequired(APIException):
    status_code = 402
    default_detail = _("Payment is required to access this resource.")
