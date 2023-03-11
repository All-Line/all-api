from apps.buying.models import ContractModel
from pipelines.base import BasePipeItem


class CreateContract(BasePipeItem):
    def _run(self):
        user = self.pipeline.user
        receipt = self.pipeline.receipt
        package = self.pipeline.package

        ContractModel.objects.create(user=user, receipt=receipt, package=package)
