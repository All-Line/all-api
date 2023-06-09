# Generated by Django 3.2.18 on 2023-04-26 22:57

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("social", "0010_auto_20230426_2246"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="missionmodel",
            name="author",
        ),
        migrations.RemoveField(
            model_name="missionmodel",
            name="is_completed",
        ),
        migrations.AlterField(
            model_name="eventmodel",
            name="require_login_answers",
            field=models.BooleanField(
                default=False,
                help_text=(
                    "Go to 'Login Questions' session to add questions that will"
                    " be asked to the guests before they can answer the event."
                ),
                verbose_name="Require Login Answers",
            ),
        ),
    ]
