from django.contrib.auth.models import UserManager as DefaultManager
from django.db import models


class UserForRetentionManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(is_deleted=True)


class UserManager(DefaultManager):
    def get_queryset(self, *args, **kwargs):
        return (
            super()
            .get_queryset(*args, **kwargs)
            .filter(is_active=True, is_deleted=False)
        )
