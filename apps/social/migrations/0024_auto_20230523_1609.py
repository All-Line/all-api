# Generated by Django 3.2.18 on 2023-05-23 16:09

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("social", "0023_alter_missionmodel_thumbnail"),
    ]

    operations = [
        migrations.AddField(
            model_name="eventmodel",
            name="smtp_email",
            field=models.EmailField(
                blank=True, max_length=254, null=True, verbose_name="SMTP Email"
            ),
        ),
        migrations.AlterField(
            model_name="eventmodel",
            name="guests",
            field=models.TextField(
                blank=True,
                help_text=(
                    "\n            Enter guests in the following format:"
                    "\n            <br>"
                    "\n            email,email,email,email,..."
                    "\n            <br>"
                    "\n            (Separeted by commas)"
                    "\n        "
                ),
                null=True,
                verbose_name="Guests",
            ),
        ),
    ]
