from random import randint

from apps.user.models import UserModel
from pipelines.base import BasePipeItem


class GenerateRandomUsername(BasePipeItem):
    def _generate_random_username(self):
        first_name = self.pipeline.first_name.lower()
        last_name = self.pipeline.last_name.lower()

        numbers = f"{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}"

        username = f"{first_name}-{last_name}-{numbers}"

        try:
            UserModel.objects.get(username=username)
            self._generate_random_username()  # pragma: nocover
        except UserModel.DoesNotExist:
            return username

    def _run(self):
        if self.pipeline.username is None:
            self.pipeline.username = self._generate_random_username()
