import requests
from decouple import config as env

from apps.buying.backends.base import BaseBackend


class AppleBackend(BaseBackend):
    def _is_valid_receipt(self, receipt):
        endpoint = "https://buy.itunes.apple.com/verifyReceipt"
        payload = {"receipt-data": receipt, "password": env("APPLE_SHARED_SECRET")}
        valid_apple_status = 0

        response = requests.post(endpoint, json=payload)

        return response.json()["status"] == valid_apple_status
