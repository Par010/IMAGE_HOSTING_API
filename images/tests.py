from datetime import timedelta
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from PIL import Image as PILImage

from image_hosting_api.users.models import User
from plans.models import Plan, UserPlan

from .models import Image, Thumbnail


class ImageThumbnailServeViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@gmail.com",
            password="testpassword",
        )
        self.plan = Plan.objects.create(
            name="Enterprise Test",
            thumbnail_sizes=[
                {
                    "height": 200,
                    "width": 200,
                }
            ],
            include_original_link=True,
            generate_expiring_links=True,
        )
        # create a UserPlan for testing
        self.user_plan = UserPlan.objects.create(user=self.user, plan=self.plan)

        # Create a temporary image file
        image = PILImage.new("RGB", (600, 600))
        image_io = BytesIO()
        image.save(image_io, format="JPEG")
        image_file = SimpleUploadedFile("test_image.jpg", image_io.getvalue(), content_type="image/jpeg")

        # create an Image for testing
        self.image = Image.objects.create(
            user=self.user_plan,
            title="Test Image",
            image=image_file,
            expiry_in_seconds=300,
        )
        self.image.save()

    def test_serve_image(self):
        url = reverse("images:serve_image", kwargs={"uuid": str(self.image.uuid)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_serve_expired_image(self):
        self.image.expiry_in_seconds = 1
        self.image.upload_time = timezone.now() - timedelta(seconds=2)
        self.image.save()

        url = reverse("images:serve_image", kwargs={"uuid": str(self.image.uuid)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_serve_thumbnail(self):
        thumbnails = Thumbnail.objects.filter(image=self.image)
        for thumbnail in thumbnails:
            url = reverse("images:serve_thumbnail", kwargs={"uuid": str(thumbnail.uuid)})
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
