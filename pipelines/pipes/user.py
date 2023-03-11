from django.contrib.auth.hashers import make_password

from pipelines.base import BasePipeline
from pipelines.items import (
    CreateUser,
    GenerateRandomUsername,
    GenerateToken,
    SendEmailToVerification,
)


class CreateUserPipeline(BasePipeline):
    def __init__(
        self,
        first_name,
        last_name,
        email,
        password,
        service,
        username=None,
        birth_date=None,
        document=None,
        country=None,
        profile_image=None,
    ):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = make_password(password)
        self.service = service
        self.username = username
        self.birth_date = birth_date
        self.document = document
        self.country = country
        self.profile_image = profile_image

        super().__init__(
            steps=[
                GenerateRandomUsername,
                CreateUser,
                GenerateToken,
                SendEmailToVerification,
            ]
        )
