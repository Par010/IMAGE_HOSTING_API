from datetime import timedelta
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from PIL import Image as PILImage
from rest_framework import status
from rest_framework.test import APIClient

from plans.models import Plan, UserPlan

from .models import Image, Thumbnail

User = get_user_model()


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

        # create a temporary image file
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


class ImageUploadViewSetTests(TestCase):
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
                },
                {
                    "height": 400,
                    "width": 400,
                },
            ],
            include_original_link=True,
            generate_expiring_links=True,
        )
        self.user_plan = UserPlan.objects.create(user=self.user, plan=self.plan)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_upload_image(self):
        url = reverse("api:image_upload-list")
        # create a temporary image file
        image = PILImage.new("RGB", (600, 600))
        image_io = BytesIO()
        image.save(image_io, format="JPEG")
        image_file = SimpleUploadedFile("test_image.jpg", image_io.getvalue(), content_type="image/jpeg")

        image_data = {"title": "Test Image", "image": image_file}
        response = self.client.post(url, image_data, format="multipart")
        response_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Image.objects.count(), 1)
        self.assertEqual(Image.objects.first().title, "Test Image")
        # check if original_image key exists in response JSON
        self.assertIn("original_image", response_data)
        # check if thumbnails key exists in response JSON
        self.assertIn("thumbnails", response_data)
        thumbnails = response_data.get("thumbnails", {})
        # check if 200x200 and 400x400 thumbnails exist in response JSON
        self.assertIn("200x200", thumbnails)
        self.assertIn("400x400", thumbnails)

    def test_upload_image_with_invlaid_expiry(self):
        url = reverse("api:image_upload-list")
        # create a temporary image file
        image = PILImage.new("RGB", (600, 600))
        image_io = BytesIO()
        image.save(image_io, format="JPEG")
        image_file = SimpleUploadedFile("test_image.jpg", image_io.getvalue(), content_type="image/jpeg")

        image_data = {"title": "Test Image", "image": image_file, "expiry_in_seconds": 30}
        response = self.client.post(url, image_data, format="multipart")
        response_data = response.json()
        print(response_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_data["expiry_in_seconds"], ["Expiry time needs to be between 300 and 30000 seconds"])


class ImageListViewSetTests(TestCase):
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
                },
                {
                    "height": 400,
                    "width": 400,
                },
            ],
            include_original_link=True,
            generate_expiring_links=True,
        )
        self.user_plan = UserPlan.objects.create(user=self.user, plan=self.plan)

        # create a temporary image file
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

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_list_images(self):
        url = reverse("api:image_list-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Test Image")

    def test_list_images_permission(self):
        # turn generate_expiring_links False in Plan
        self.plan.generate_expiring_links = False
        self.plan.save()
        url = reverse("api:image_list-list")
        response = self.client.get(url)

        # check if the endpoint raises 403
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
