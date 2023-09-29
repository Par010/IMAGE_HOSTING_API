from django.urls import path

from . import views

app_name = "images"
urlpatterns = [
    path("images/<uuid:uuid>/", views.serve_image, name="serve_image"),
    path("thumbnails/<uuid:uuid>/", views.serve_thumbnail, name="serve_thumbnail"),
]
