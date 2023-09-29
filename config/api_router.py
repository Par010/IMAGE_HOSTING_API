from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from image_hosting_api.users.api.views import UserViewSet
from images.api.views import ImageViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)
router.register("images", ImageViewSet, basename="image")


app_name = "api"
urlpatterns = router.urls
