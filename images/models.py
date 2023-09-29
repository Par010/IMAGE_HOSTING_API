import os
import uuid
from io import BytesIO

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.utils import timezone
from PIL import Image as PILImage

from plans.models import UserPlan

from .utils import generate_radom_string


def upload_original_image(instance, filename):
    return os.path.join(
        "images/original",
        instance.user.user.email,
        instance.user.plan.name,
        # adding a random string to avoid users accessing media url directly
        generate_radom_string(),
        filename,
    )


def upload_thumbnail(instance, filename):
    return os.path.join(
        "images/thumbnails",
        instance.image.user.user.email,
        instance.image.user.plan.name,
        f"{instance.height}x{instance.width}",
        generate_radom_string(),
        filename,
    )


class Thumbnail(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    image = models.ForeignKey("Image", related_name="thumbnail_image", on_delete=models.CASCADE)
    height = models.PositiveIntegerField()
    width = models.PositiveIntegerField()
    thumbnail = models.ImageField(upload_to=upload_thumbnail)

    def __str__(self):
        return f"{self.image.title}_{self.height}x{self.width}"


class Image(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    user = models.ForeignKey(UserPlan, related_name="image_user_plan", on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to=upload_original_image)
    upload_time = models.DateTimeField(auto_now_add=True)
    expiry_in_seconds = models.PositiveIntegerField(
        blank=True, null=True, help_text="Optional expiry time in seconds, needs to be between 300 and 30000 if used"
    )

    def __str__(self):
        return f"{self.user.user.email}-{self.user.plan.name}-{self.title}"

    def clean(self):
        super().clean()

        if self.expiry_in_seconds is not None:
            if self.expiry_in_seconds < 300 or self.expiry_in_seconds > 30000:
                raise ValidationError("Expiry time needs to be between 300 and 30000 seconds")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # open uploaded image
        img = PILImage.open(self.image.path)

        # get thumbnail options for the user's Plans
        thumbnails = self.user.plan.thumbnail_sizes

        for thumbnail in thumbnails:
            height = thumbnail["height"]
            width = thumbnail["width"]

            # resize the image
            thumbnail = img.resize((height, width))

            # convert resized image to binary data
            buffer = BytesIO()
            thumbnail.save(buffer, format="JPEG")

            # create an InMemoryUploadedFile and assign it to the thumbnail field
            buffer.seek(0)
            thumbnail_file = InMemoryUploadedFile(
                buffer, None, os.path.basename(self.image.name), "image/jpeg", buffer.tell(), None
            )

            # create the Thumbnail instance
            thumbnail_instance = Thumbnail(image=self, height=height, width=width, thumbnail=thumbnail_file)

            thumbnail_instance.save()

    def is_expired(self):
        if not self.expiry_in_seconds:
            return False
        expiry_datetime = self.upload_time + timezone.timedelta(seconds=self.expiry_in_seconds)
        return timezone.now() >= expiry_datetime
