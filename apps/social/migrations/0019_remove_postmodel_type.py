# Generated by Django 3.2.18 on 2023-05-20 01:01

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("social", "0018_auto_20230518_1730"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="postmodel",
            name="type",
        ),
    ]
