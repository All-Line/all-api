from pipelines.mail_sender.dummy_sender import DummySender
from pipelines.mail_sender.sendgrid_sender import SendGridSender

SENDER_BACKENDS = {"sendgrid": SendGridSender, "dummy": DummySender}
