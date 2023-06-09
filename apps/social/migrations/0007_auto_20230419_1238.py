# Generated by Django 3.2.16 on 2023-04-19 12:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("social", "0006_auto_20230419_1229"),
    ]

    operations = [
        migrations.AlterField(
            model_name="eventmodel",
            name="event_link",
            field=models.URLField(
                blank=True,
                help_text="Link for guests to access the event",
                null=True,
                verbose_name="Event Link",
            ),
        ),
        migrations.AlterField(
            model_name="eventmodel",
            name="guests",
            field=models.TextField(
                blank=True,
                help_text="\n            Enter guests in the following format:\n            <br>\n            email,password<br>\n            email,password<br>\n            email,password<br>\n            ...\n        ",
                null=True,
                verbose_name="Guests",
            ),
        ),
    ]
