from rest_framework.authtoken.models import Token

from pipelines.base import BasePipeItem


class GenerateToken(BasePipeItem):
    def _run(self):
        user = self.pipeline.user
        self.pipeline.token = Token.objects.get_or_create(user=user)[0].key
