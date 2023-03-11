from pipelines.base import BasePipeline
from pipelines.items.create_contract import CreateContract
from pipelines.items.encrypt_receipt import EncryptReceipt
from pipelines.items.set_user_premium import SetUserPremium


class CreateContractPipeline(BasePipeline):
    def __init__(
        self,
        receipt,
        package,
        user,
    ):
        self.receipt = receipt
        self.package = package
        self.user = user

        super().__init__(steps=[EncryptReceipt, SetUserPremium, CreateContract])
