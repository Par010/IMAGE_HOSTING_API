from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from image_hosting_api.users.api.views import UserViewSet
from images.api.views import ImageListViewSet, ImageUploadViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)
router.register("images", ImageUploadViewSet, basename="image_upload")
router.register("get/images", ImageListViewSet, basename="image_list")


app_name = "api"
urlpatterns = router.urls
