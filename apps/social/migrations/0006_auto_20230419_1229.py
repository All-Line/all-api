# Generated by Django 3.2.16 on 2023-04-19 12:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("social", "0005_auto_20230419_1225"),
    ]

    operations = [
        migrations.AddField(
            model_name="eventmodel",
            name="event_link",
            field=models.URLField(
                blank=True, null=True, verbose_name="Event Link"
            ),
        ),
        migrations.AlterField(
            model_name="eventmodel",
            name="send_email_to_guests",
            field=models.BooleanField(
                default=False,
                help_text="Send email to guests with their credentials",
                verbose_name="Send email to guests",
            ),
        ),
    ]
