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
        send_mail=False,
        **kwargs,
    ):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = make_password(password)
        self.service = service
        self.username = username
        self.send_mail = send_mail
        self.kwargs = kwargs

        super().__init__(
            steps=[
                GenerateRandomUsername,
                CreateUser,
                GenerateToken,
                SendEmailToVerification,
            ]
        )
