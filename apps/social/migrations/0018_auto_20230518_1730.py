# Generated by Django 3.2.18 on 2023-05-18 17:30

from django.db import migrations, models

import apps.social.models


class Migration(migrations.Migration):

    dependencies = [
        ("social", "0017_alter_reactiontypemodel_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="missionmodel",
            name="thumbnail",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to=apps.social.models.mission_directory_path,
                verbose_name="Thumbnail",
            ),
        ),
        migrations.AlterField(
            model_name="eventmodel",
            name="event_type",
            field=models.CharField(
                choices=[("open", "Open"), ("closed", "Closed")],
                default="closed",
                help_text=(
                    'This property, when "Open", allows anyone to access the '
                    'event. When "Closed", a certain group will only be '
                    'able to access the event: fill in the "Guests" field in '
                    "this case."
                ),
                max_length=255,
                verbose_name="Event Type",
            ),
        ),
    ]