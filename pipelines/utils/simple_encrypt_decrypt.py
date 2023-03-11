import base64
import binascii


class SimpleEncryptDecrypt:
    def __init__(self, value):
        self.value = value
        self.is_encrypted = False

    @property
    def encrypted_value(self):
        return self.get_encrypted_value()

    @property
    def decrypted_value(self):
        return self.get_decrypted_value()

    def get_encrypted_value(self):
        value_bytes = self.value.encode("ascii")
        base64_bytes = base64.b64encode(value_bytes)
        encoded_value = base64_bytes.decode()

        return encoded_value

    def get_decrypted_value(self):
        try:
            base64_bytes = self.value.encode("ascii")
            value_bytes = base64.b64decode(base64_bytes)
            decoded_value = value_bytes.decode("utf-8")

            return decoded_value
        except binascii.Error:
            return self.value

    def encrypt(self):
        if not self.is_encrypted:
            encoded_value = self.get_encrypted_value()

            self.value = encoded_value
            self.is_encrypted = True

    def decrypt(self):
        if self.is_encrypted:
            decoded_value = self.get_decrypted_value()

            self.value = decoded_value
            self.is_encrypted = False

    @staticmethod
    def base64_encrypt(value):
        value_bytes = value.encode("ascii")
        base64_bytes = base64.b64encode(value_bytes)
        encoded_value = base64_bytes.decode()

        return encoded_value

    @staticmethod
    def base64_decrypt(value):
        try:
            base64_bytes = value.encode("ascii")
            value_bytes = base64.b64decode(base64_bytes)
            decoded_value = value_bytes.decode("utf-8")

            return decoded_value
        except binascii.Error:
            return value

    def check_base64(self, value: str) -> bool:
        return self.get_decrypted_value() == value
