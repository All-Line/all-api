from pipelines.base import BasePipeline
from pipelines.items import CreateUser, GenerateRandomUsername, GenerateToken, SendEmail
from pipelines.items.add_mention_on_comment import AddMentionOnComment


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
        email_type=None,
        **kwargs,
    ):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.service = service
        self.username = username
        self.send_mail = send_mail
        self.email_type = email_type
        self.kwargs = kwargs

        super().__init__(
            steps=[
                GenerateRandomUsername,
                CreateUser,
                GenerateToken,
                SendEmail,
            ]
        )


class MentionGuestPipeline(BasePipeline):
    def __init__(self, user, comment):
        self.user = user
        self.comment = comment
        self.email_type = "mention_notification"
        self.send_mail = True

        super().__init__(
            steps=[
                AddMentionOnComment,
                SendEmail,
            ]
        )


class NotifyGuestNewPostPipeline(BasePipeline):
    def __init__(self, user):
        self.user = user
        self.email_type = "new_post_notification"
        self.send_mail = True

        super().__init__(
            steps=[
                SendEmail,
            ]
        )
