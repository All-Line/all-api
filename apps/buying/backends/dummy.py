from apps.buying.backends.base import BaseBackend


class DummyBackend(BaseBackend):
    def _is_valid_receipt(self, receipt):
        DUMMY_VALID_RECEIPT = "dummy_receipt"

        return receipt == DUMMY_VALID_RECEIPT
