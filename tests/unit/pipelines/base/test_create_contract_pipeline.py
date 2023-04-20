from unittest.mock import Mock

from pipelines.items.create_contract import CreateContract
from pipelines.items.encrypt_receipt import EncryptReceipt
from pipelines.items.set_user_premium import SetUserPremium
from pipelines.pipes.contract import CreateContractPipeline


class TestCreateContractPipeline:
    def test_init(self):
        mock_receipt = Mock()
        mock_package = Mock()
        mock_user = Mock()
        create_contract = CreateContractPipeline(
            mock_receipt, mock_package, mock_user
        )

        assert create_contract.receipt == mock_receipt
        assert create_contract.package == mock_package
        assert create_contract.user == mock_user
        assert create_contract.steps == [
            EncryptReceipt,
            SetUserPremium,
            CreateContract,
        ]
