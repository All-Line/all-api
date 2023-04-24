from random import randint

from apps.user.models import UserModel
from pipelines.base import BasePipeItem


class GenerateRandomUsername(BasePipeItem):
    def _generate_random_username(self):
        service_slug = self.pipeline.service.slug

        numbers = f"{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}"

        username = f"{service_slug}-{numbers}"

        try:
            UserModel.objects.get(username=username)
            self._generate_random_username()  # pragma: nocover
        except UserModel.DoesNotExist:
            return username

    def _run(self):
        if self.pipeline.username is None:
            self.pipeline.username = self._generate_random_username()
