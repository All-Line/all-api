from pipelines.base import BasePipeline
from pipelines.items import (
    CreateUser,
    GenerateRandomUsername,
    GenerateToken,
    SendEmailToVerification,
)
from pipelines.pipes import CreateUserPipeline


class TestCreateUserPipeline:
    @classmethod
    def setup_class(cls):
        cls.pipeline = CreateUserPipeline
        cls.base_pipeline_data = {
            "first_name": "some_first_name",
            "last_name": "some_last_name",
            "email": "some_email",
            "password": "some_password",
            "service": "some_service",
            "birth_date": "some_birth_date",
        }

    def test_parent_class(self):
        assert issubclass(self.pipeline, BasePipeline)

    def test_init(self):
        user_create_pipeline = self.pipeline(**self.base_pipeline_data)

        assert user_create_pipeline.first_name == "some_first_name"
        assert user_create_pipeline.last_name == "some_last_name"
        assert user_create_pipeline.email == "some_email"
        assert user_create_pipeline.password == "some_password"
        assert user_create_pipeline.service == "some_service"
        assert user_create_pipeline.kwargs == {
            "birth_date": "some_birth_date",
        }

    def test_pipelines_items(self):
        user_create_pipeline = self.pipeline(**self.base_pipeline_data)

        steps = user_create_pipeline.steps
        assert steps == [
            GenerateRandomUsername,
            CreateUser,
            GenerateToken,
            SendEmailToVerification,
        ]
