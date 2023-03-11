from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    date_modified = models.DateTimeField(_("date modified"), default=timezone.now)

    class Meta:
        abstract = True
