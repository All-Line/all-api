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
            password=pipeline.password,
            service=pipeline.service,
            birth_date=pipeline.birth_date,
            document=pipeline.document,
            country=pipeline.country,
            profile_image=pipeline.profile_image,
        )

        self.pipeline.user = user

        self.log(
            f"A new user was created: {user.first_name} {user.last_name} ({user.id})"
        )
