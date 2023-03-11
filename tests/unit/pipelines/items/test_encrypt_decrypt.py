from unittest.mock import Mock, patch

from pipelines.base import BasePipeItem
from pipelines.items.encrypt_receipt import EncryptReceipt


class TestEncryptReceipt:
    @classmethod
    def setup_class(cls):
        cls.item = EncryptReceipt

    def test_parent_class(self):
        assert issubclass(self.item, BasePipeItem)

    @patch("pipelines.utils.simple_encrypt_decrypt.SimpleEncryptDecrypt.base64_encrypt")
    def test_run(self, mock_base64_encrypt):
        pipeline = Mock(receipt="receipt")
        item = self.item(pipeline)
        item._run()

        mock_base64_encrypt.assert_called_once_with("receipt")
        assert pipeline.receipt == mock_base64_encrypt.return_value
