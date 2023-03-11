from jose import jwt


class BaseBackend:
    def __init__(self):  # pragma: nocover
        pass

    @staticmethod
    def get_jwt(body, secret_key, algorithm, headers):
        return jwt.encode(body, secret_key, algorithm, headers)

    def _is_valid_receipt(self, receipt: str) -> bool:
        raise NotImplementedError

    def is_valid_receipt(self, receipt: str) -> bool:
        return self._is_valid_receipt(receipt)
