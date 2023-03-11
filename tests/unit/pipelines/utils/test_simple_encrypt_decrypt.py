import binascii
from unittest.mock import Mock, patch

from pipelines.utils.simple_encrypt_decrypt import SimpleEncryptDecrypt


class TestSimpleEncryptDecrypt:
    def test_init_(self):
        mock_value = Mock()
        simple_encrypt_decrypt = SimpleEncryptDecrypt(mock_value)

        assert simple_encrypt_decrypt.value == mock_value
        assert simple_encrypt_decrypt.is_encrypted is False

    @patch(
        "pipelines.utils.simple_encrypt_decrypt."
        "SimpleEncryptDecrypt.get_encrypted_value"
    )
    def test_encrypted_value_property(self, mock_get_encrypted_value):
        mock_value = Mock()
        simple_encrypt_decrypt = SimpleEncryptDecrypt(mock_value)
        encrypted_value = simple_encrypt_decrypt.encrypted_value

        mock_get_encrypted_value.assert_called_once()
        assert encrypted_value == mock_get_encrypted_value.return_value

    @patch(
        "pipelines.utils.simple_encrypt_decrypt."
        "SimpleEncryptDecrypt.get_decrypted_value"
    )
    def test_decrypted_value_property(self, mock_get_decrypted_value):
        mock_value = Mock()
        simple_encrypt_decrypt = SimpleEncryptDecrypt(mock_value)
        encrypted_value = simple_encrypt_decrypt.decrypted_value

        mock_get_decrypted_value.assert_called_once()
        assert encrypted_value == mock_get_decrypted_value.return_value

    @patch("pipelines.utils.simple_encrypt_decrypt.base64.b64encode")
    def test_get_encrypted_value(self, mock_b64encode):
        mock_value = Mock()
        simple_encrypt_decrypt = SimpleEncryptDecrypt(mock_value)
        result = simple_encrypt_decrypt.get_encrypted_value()

        mock_value.encode.assert_called_once_with("ascii")
        mock_b64encode.assert_called_once_with(mock_value.encode.return_value)
        mock_b64encode.return_value.decode.assert_called_once()
        assert result == mock_b64encode.return_value.decode.return_value

    @patch("pipelines.utils.simple_encrypt_decrypt.base64.b64decode")
    def test_get_decrypted_value(self, mock_b64decode):
        mock_value = Mock()
        simple_encrypt_decrypt = SimpleEncryptDecrypt(mock_value)
        result = simple_encrypt_decrypt.get_decrypted_value()

        mock_value.encode.assert_called_once_with("ascii")
        mock_b64decode.assert_called_once_with(mock_value.encode.return_value)
        mock_b64decode.return_value.decode.assert_called_once_with("utf-8")
        assert result == mock_b64decode.return_value.decode.return_value

    @patch("pipelines.utils.simple_encrypt_decrypt.base64.b64decode")
    def test_get_decrypted_value_with_value_not_encrypted(self, mock_b64decode):
        mock_value = Mock()
        simple_encrypt_decrypt = SimpleEncryptDecrypt(mock_value)
        mock_b64decode.side_effect = binascii.Error
        result = simple_encrypt_decrypt.get_decrypted_value()

        assert result == mock_value

    @patch(
        "pipelines.utils.simple_encrypt_decrypt."
        "SimpleEncryptDecrypt.get_encrypted_value"
    )
    def test_encrypt(self, mock_get_encrypted_value):
        mock_value = Mock()
        simple_encrypt_decrypt = SimpleEncryptDecrypt(mock_value)
        simple_encrypt_decrypt.encrypt()

        mock_get_encrypted_value.assert_called_once()
        assert simple_encrypt_decrypt.value == mock_get_encrypted_value.return_value
        assert simple_encrypt_decrypt.is_encrypted is True

    @patch(
        "pipelines.utils.simple_encrypt_decrypt."
        "SimpleEncryptDecrypt.get_encrypted_value"
    )
    def test_encrypt_with_value_already_encrypted(self, mock_get_encrypted_value):
        mock_value = Mock()
        simple_encrypt_decrypt = SimpleEncryptDecrypt(mock_value)
        simple_encrypt_decrypt.is_encrypted = True
        result = simple_encrypt_decrypt.encrypt()

        mock_get_encrypted_value.not_assert_called_once()
        assert result is None

    @patch(
        "pipelines.utils.simple_encrypt_decrypt."
        "SimpleEncryptDecrypt.get_decrypted_value"
    )
    def test_decrypt(self, mock_get_decrypted_value):
        mock_value = Mock()
        simple_encrypt_decrypt = SimpleEncryptDecrypt(mock_value)
        simple_encrypt_decrypt.is_encrypted = True
        simple_encrypt_decrypt.decrypt()

        mock_get_decrypted_value.assert_called_once()
        assert simple_encrypt_decrypt.value == mock_get_decrypted_value.return_value
        assert simple_encrypt_decrypt.is_encrypted is False

    @patch(
        "pipelines.utils.simple_encrypt_decrypt."
        "SimpleEncryptDecrypt.get_decrypted_value"
    )
    def test_decrypt_with_value_not_encrypted(self, mock_get_decrypted_value):
        mock_value = Mock()
        simple_encrypt_decrypt = SimpleEncryptDecrypt(mock_value)
        result = simple_encrypt_decrypt.decrypt()

        mock_get_decrypted_value.not_assert_called_once()
        assert result is None

    @patch("pipelines.utils.simple_encrypt_decrypt.base64.b64encode")
    def test_base64_encrypt(self, mock_b64encode):
        mock_value = Mock()
        result = SimpleEncryptDecrypt.base64_encrypt(mock_value)

        mock_value.encode.assert_called_once_with("ascii")
        mock_b64encode.assert_called_once_with(mock_value.encode.return_value)
        mock_b64encode.return_value.decode.assert_called_once()
        assert result == mock_b64encode.return_value.decode.return_value

    @patch("pipelines.utils.simple_encrypt_decrypt.base64.b64decode")
    def test_base64_decrypt(self, mock_b64decode):
        mock_value = Mock()
        result = SimpleEncryptDecrypt.base64_decrypt(mock_value)

        mock_value.encode.assert_called_once_with("ascii")
        mock_b64decode.assert_called_once_with(mock_value.encode.return_value)
        mock_b64decode.return_value.decode.assert_called_once_with("utf-8")
        assert result == mock_b64decode.return_value.decode.return_value

    @patch("pipelines.utils.simple_encrypt_decrypt.base64.b64decode")
    def test_base64_decrypt_with_value_not_encrypted(self, mock_b64decode):
        mock_value = Mock()
        mock_b64decode.side_effect = binascii.Error
        result = SimpleEncryptDecrypt.base64_decrypt(mock_value)

        mock_value.encode.not_assert_called()
        mock_b64decode.not_assert_called()
        mock_b64decode.return_value.decode.not_assert_called()
        assert result == mock_value

    @patch(
        "pipelines.utils.simple_encrypt_decrypt."
        "SimpleEncryptDecrypt.get_decrypted_value"
    )
    def test_check_base64(self, mock_get_decrypted_value):
        mock_value_decrypt = Mock()
        mock_get_decrypted_value.return_value = mock_value_decrypt
        mock_value = Mock()
        simple_encrypt_decrypt = SimpleEncryptDecrypt(mock_value)
        simple_encrypt_decrypt.check_base64(mock_value_decrypt)

        mock_get_decrypted_value.assert_called_once()
        assert mock_get_decrypted_value.return_value == mock_value_decrypt

    @patch(
        "pipelines.utils.simple_encrypt_decrypt."
        "SimpleEncryptDecrypt.get_decrypted_value"
    )
    def test_check_base64_with_value_decrypted_not_equal(
        self, mock_get_decrypted_value
    ):
        mock_value_decrypt = Mock()
        mock_value = Mock()
        simple_encrypt_decrypt = SimpleEncryptDecrypt(mock_value)
        simple_encrypt_decrypt.check_base64(mock_value_decrypt)

        mock_get_decrypted_value.assert_called_once()
