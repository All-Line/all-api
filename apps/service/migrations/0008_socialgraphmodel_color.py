# Generated by Django 3.2.25 on 2024-04-07 07:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("visual_structure", "0002_alter_colormodel_color"),
        ("service", "0007_auto_20240407_0708"),
    ]

    operations = [
        migrations.AddField(
            model_name="socialgraphmodel",
            name="color",
            field=models.ForeignKey(
                blank=True,
                help_text=(
                    "The color that will be used to generate the graph image. "
                    "If empty, the default color (##66c2a5) will be used."
                ),
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="social_graphs",
                to="visual_structure.colormodel",
                verbose_name="Color",
            ),
        ),
    ]
