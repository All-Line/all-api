from pipelines.base import BasePipeItem
from pipelines.utils.simple_encrypt_decrypt import SimpleEncryptDecrypt


class EncryptReceipt(BasePipeItem):
    def _run(self):
        receipt = self.pipeline.receipt
        encrypted_receipt = SimpleEncryptDecrypt.base64_encrypt(receipt)

        self.pipeline.receipt = encrypted_receipt
