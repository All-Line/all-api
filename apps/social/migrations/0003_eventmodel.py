# Generated by Django 3.2.16 on 2023-04-19 02:36

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models

import apps.social.models


class Migration(migrations.Migration):
    dependencies = [
        ("service", "0001_initial"),
        ("social", "0002_postcommentmodel"),
    ]

    operations = [
        migrations.CreateModel(
            name="EventModel",
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
                ("is_active", models.BooleanField(default=True)),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        verbose_name="date joined",
                    ),
                ),
                (
                    "date_modified",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        verbose_name="date modified",
                    ),
                ),
                (
                    "title",
                    models.CharField(max_length=255, verbose_name="Title"),
                ),
                (
                    "description",
                    models.TextField(blank=True, null=True, verbose_name="Description"),
                ),
                (
                    "attachment",
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to=apps.social.models.post_attachment_directory_path,
                        verbose_name="Attachment",
                    ),
                ),
                (
                    "event_type",
                    models.CharField(
                        choices=[("open", "Open"), ("closed", "Closed")],
                        default="closed",
                        max_length=255,
                        verbose_name="Event Type",
                    ),
                ),
                (
                    "guests",
                    models.TextField(
                        blank=True,
                        help_text="\n\n            Enter guests in the following format:\n            \n            email,password\n            email,password\n            email,password\n            ...\n        ",
                        null=True,
                        verbose_name="Guests",
                    ),
                ),
                (
                    "service",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="events",
                        to="service.servicemodel",
                        verbose_name="Service",
                    ),
                ),
            ],
            options={
                "verbose_name": "Event",
                "verbose_name_plural": "Events",
            },
        ),
    ]
