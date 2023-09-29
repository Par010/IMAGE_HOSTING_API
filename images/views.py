from django.http import FileResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404

from .models import Image, Thumbnail


def serve_image(request, uuid):
    # fetch the Image object based on the UUID
    image = get_object_or_404(Image, uuid=uuid)

    # check if image has already expired
    if image.is_expired():
        return HttpResponseNotFound("Image has expired!")

    response = FileResponse(image.image, content_type="image/jpeg")
    return response


def serve_thumbnail(request, uuid):
    # fetch the Image object based on the UUID
    thumbnail = get_object_or_404(Thumbnail, uuid=uuid)

    response = FileResponse(thumbnail.thumbnail, content_type="image/jpeg")
    return response
