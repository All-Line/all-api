from django.contrib.auth.hashers import make_password

from apps.user.models import UserModel
from pipelines.base import BasePipeItem


class CreateUser(BasePipeItem):
    def _run(self):
        pipeline = self.pipeline
        user = UserModel.objects.create(
            username=pipeline.username,
            first_name=pipeline.first_name,
            last_name=pipeline.last_name,
            email=pipeline.email,
            password=make_password(pipeline.password),
            service=pipeline.service,
            **pipeline.kwargs,
        )

        self.pipeline.user = user

        self.log(
            f"A new user was created: {user.first_name} {user.last_name} ({user.id})"
        )
