from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.buying.backends import BACKENDS
from apps.material.models import CourseModel
from apps.service.models import ServiceModel
from apps.user.models import UserModel
from utils.abstract_models.base_model import BaseModel


class StoreModel(BaseModel):
    BACKEND_CHOICES = (("dummy", _("Dummy Backend")), ("apple", _("Apple Backend")))

    name = models.CharField(verbose_name=_("Title"), max_length=255, unique=True)
    backend = models.CharField(
        verbose_name=_("Integration Backend"), max_length=255, choices=BACKEND_CHOICES
    )

    class Meta:
        verbose_name = _("Store")
        verbose_name_plural = _("Stores")

    def __str__(self):
        return self.name

    def get_backend(self):
        backend = BACKENDS[self.backend]
        return backend()


class PackageModel(BaseModel):
    label = models.CharField(verbose_name=_("Label"), max_length=255)
    price = models.FloatField(verbose_name=_("Price"))
    slug = models.SlugField(verbose_name=_("Slug"))
    store = models.ForeignKey(
        StoreModel,
        related_name="packages",
        verbose_name=_("Store"),
        on_delete=models.CASCADE,
    )
    courses = models.ManyToManyField(
        CourseModel, related_name="packages", verbose_name=_("Courses")
    )
    service = models.ForeignKey(
        ServiceModel,
        related_name="packages",
        verbose_name=_("Service"),
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _("Package")
        verbose_name_plural = _("Packages")

    def __str__(self):
        return self.label


class ContractModel(BaseModel):
    receipt = models.TextField(verbose_name=_("Receipt"))
    package = models.ForeignKey(
        PackageModel,
        verbose_name=_("Package"),
        related_name="contracts",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        UserModel,
        verbose_name=_("User"),
        related_name="contracts",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _("Contract")
        verbose_name_plural = _("Contracts")

    def __str__(self):
        return f"Contract for {self.user.first_name} {self.user.last_name}"
