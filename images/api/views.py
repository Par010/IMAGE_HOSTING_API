from rest_framework import status
from rest_framework.mixins import CreateModelMixin
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet

from images.models import Image

from .permissions import CanAccessImageListViewSet
from .serializers import ImageListSerializer, ImageUploadSerializer


class ImageUploadViewSet(CreateModelMixin, GenericViewSet):
    parser_classes = (MultiPartParser,)
    serializer_class = ImageUploadSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ImageListViewSet(ReadOnlyModelViewSet):
    serializer_class = ImageListSerializer
    permission_classes = [CanAccessImageListViewSet]

    def get_queryset(self):
        user = self.request.user
        return Image.objects.filter(user__user=user)
