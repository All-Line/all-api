# Generated by Django 3.2.18 on 2023-05-26 14:36

from django.db import migrations, models

import apps.social.models


class Migration(migrations.Migration):
    dependencies = [
        ("social", "0025_auto_20230526_1429"),
    ]

    operations = [
        migrations.AddField(
            model_name="reactiontypemodel",
            name="clicked_image",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to=apps.social.models.post_attachment_directory_path,
                verbose_name="Clicked Image",
            ),
        ),
    ]