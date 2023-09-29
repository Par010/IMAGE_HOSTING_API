from rest_framework import status
from rest_framework.mixins import CreateModelMixin
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .serializers import ImageUploadSerializer


class ImageViewSet(CreateModelMixin, GenericViewSet):
    parser_classes = (MultiPartParser,)
    serializer_class = ImageUploadSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
