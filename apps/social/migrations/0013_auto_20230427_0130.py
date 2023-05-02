# Generated by Django 3.2.18 on 2023-04-27 01:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("service", "0002_serviceclientmodel"),
        ("social", "0012_missionmodel_service_client"),
    ]

    operations = [
        migrations.AddField(
            model_name="loginquestionoption",
            name="order",
            field=models.PositiveIntegerField(default=0, verbose_name="Order"),
        ),
        migrations.AddField(
            model_name="loginquestions",
            name="order",
            field=models.PositiveIntegerField(default=0, verbose_name="Order"),
        ),
        migrations.AlterField(
            model_name="missionmodel",
            name="service_client",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="missions",
                to="service.serviceclientmodel",
                verbose_name="Client",
            ),
        ),
    ]
