from pipelines.base import BasePipeItem


class SetUserPremium(BasePipeItem):
    def _run(self):
        user = self.pipeline.user
        user.is_premium = True
        user.save()
