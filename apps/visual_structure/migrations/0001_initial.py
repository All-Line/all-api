# Generated by Django 3.2.16 on 2022-11-25 20:26

import colorfield.fields
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ColorModel",
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
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "date_modified",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date modified"
                    ),
                ),
                ("title", models.CharField(max_length=255, verbose_name="Title")),
                (
                    "color",
                    colorfield.fields.ColorField(
                        default="#FFFFFF",
                        image_field=None,
                        max_length=18,
                        samples=None,
                        verbose_name="Color",
                    ),
                ),
            ],
            options={
                "verbose_name": "Color",
                "verbose_name_plural": "Colors",
            },
        ),
        migrations.CreateModel(
            name="ColorPaletteModel",
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
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "date_modified",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date modified"
                    ),
                ),
                ("title", models.CharField(max_length=255, verbose_name="Title")),
                (
                    "description",
                    models.TextField(blank=True, null=True, verbose_name="Description"),
                ),
                (
                    "colors",
                    models.ManyToManyField(
                        related_name="color_palettes",
                        to="visual_structure.ColorModel",
                        verbose_name="Colors",
                    ),
                ),
            ],
            options={
                "verbose_name": "Color Palette",
                "verbose_name_plural": "Color Palettes",
            },
        ),
    ]
