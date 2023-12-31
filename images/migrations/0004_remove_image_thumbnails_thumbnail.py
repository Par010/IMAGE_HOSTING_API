# Generated by Django 4.2.5 on 2023-09-29 05:47

from django.db import migrations, models
import django.db.models.deletion
import images.models


class Migration(migrations.Migration):
    dependencies = [
        ("images", "0003_image_thumbnails"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="image",
            name="thumbnails",
        ),
        migrations.CreateModel(
            name="Thumbnail",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("height", models.PositiveIntegerField()),
                ("width", models.PositiveIntegerField()),
                ("thumbnail", models.ImageField(upload_to=images.models.upload_original_image)),
                (
                    "image",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="thumbnail_image", to="images.image"
                    ),
                ),
            ],
        ),
    ]
