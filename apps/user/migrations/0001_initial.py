# Generated by Django 3.2.16 on 2022-11-25 20:26

import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models

import apps.user.managers
import apps.user.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("service", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserModel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text=(
                            "Designates that this user has all permissions without "
                            "explicitly assigning them."
                        ),
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text=(
                            "Designates whether the user can log into this admin site."
                        ),
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text=(
                            "Designates whether this user should be treated as active. "
                            "Unselect this instead of deleting accounts."
                        ),
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "is_verified",
                    models.BooleanField(default=False, verbose_name="Is Verified"),
                ),
                (
                    "is_premium",
                    models.BooleanField(default=False, verbose_name="Is Premium"),
                ),
                (
                    "is_deleted",
                    models.BooleanField(default=False, verbose_name="Is Deleted"),
                ),
                (
                    "document",
                    models.CharField(
                        blank=True, max_length=255, null=True, verbose_name="Document"
                    ),
                ),
                (
                    "email",
                    models.EmailField(max_length=254, verbose_name="Email Address"),
                ),
                (
                    "first_name",
                    models.CharField(max_length=30, verbose_name="First Name"),
                ),
                (
                    "last_name",
                    models.CharField(max_length=30, verbose_name="Last Name"),
                ),
                (
                    "username",
                    models.CharField(
                        blank=True,
                        error_messages={
                            "unique": "A user with that username already exists."
                        },
                        max_length=150,
                        null=True,
                        unique=True,
                        validators=[
                            django.contrib.auth.validators.UnicodeUsernameValidator()
                        ],
                        verbose_name="Username",
                    ),
                ),
                (
                    "birth_date",
                    models.DateField(blank=True, null=True, verbose_name="Birth Date"),
                ),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Last Login"
                    ),
                ),
                (
                    "country",
                    models.CharField(
                        blank=True, max_length=255, null=True, verbose_name="Country"
                    ),
                ),
                (
                    "profile_image",
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to=apps.user.models.profile_image_directory_path,
                        verbose_name="Profile Image",
                    ),
                ),
                (
                    "delete_reason",
                    models.TextField(
                        blank=True, null=True, verbose_name="Delete Reason"
                    ),
                ),
                (
                    "service",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="users",
                        to="service.servicemodel",
                        verbose_name="Service",
                    ),
                ),
            ],
            options={
                "verbose_name": "User",
                "verbose_name_plural": "Users",
                "unique_together": {("document", "service")},
            },
            managers=[
                ("objects", apps.user.managers.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="UserForRetentionProxy",
            fields=[],
            options={
                "verbose_name": "User for retention",
                "verbose_name_plural": "Users for retention",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("user.usermodel",),
        ),
    ]
