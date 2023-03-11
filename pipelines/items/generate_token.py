from rest_framework.authtoken.models import Token

from pipelines.base import BasePipeItem


class GenerateToken(BasePipeItem):
    def _run(self):
        user = self.pipeline.user
        Token.objects.get_or_create(user=user)
