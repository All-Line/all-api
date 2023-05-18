from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from utils.mixins.attachment_type import GetAttachmentTypeMixin


class BaseModel(models.Model):
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    date_modified = models.DateTimeField(_("date modified"), default=timezone.now)

    class Meta:
        abstract = True


class AttachmentModel:
    def __init__(self, upload_to):
        self.upload_to = upload_to

    @property
    def mixin(self):
        class Mixin(GetAttachmentTypeMixin, models.Model):
            attachment = models.FileField(
                verbose_name=_("Attachment"),
                upload_to=self.upload_to,
                null=True,
                blank=True,
            )

            class Meta:
                abstract = True

        return Mixin
