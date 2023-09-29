from django.urls import reverse
from rest_framework import serializers

from images.models import Image, Thumbnail
from plans.models import UserPlan


class ImageUploadSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=100, required=True)
    image = serializers.ImageField(required=True)

    def __init__(self, *args, **kwargs):
        context = kwargs.get("context", {})
        request = context.get("request")

        super().__init__(*args, **kwargs)

        # if request user's plan allows generate_expiring_links, then add the field to the serializer
        if request:
            user = request.user

            if UserPlan.objects.filter(user=user).exists():
                if UserPlan.objects.get(user=user).plan.generate_expiring_links:
                    self.fields["expiry_in_seconds"] = serializers.IntegerField(
                        required=False, help_text="Optional expiry time in seconds"
                    )

    def create(self, validated_data):
        # get user from request context
        request = self.context.get("request")
        user = UserPlan.objects.get(user=request.user)

        # get validated data
        title = validated_data.get("title")
        image = validated_data.get("image")
        expiry_in_seconds = validated_data.get("expiry_in_seconds", None)

        image_instance = Image.objects.create(user=user, title=title, image=image, expiry_in_seconds=expiry_in_seconds)
        return image_instance

    def to_representation(self, instance):
        response_dict = {}
        request = self.context.get("request")
        user_plan = UserPlan.objects.get(user=request.user)
        # check if user's plan allows include_original_link before including it in response
        if user_plan.plan.include_original_link:
            response_dict["original_image"] = request.build_absolute_uri(
                reverse("images:serve_image", kwargs={"uuid": instance.uuid})
            )

        # fetch the thumbnails related to the image created and add to response
        thumbnails = Thumbnail.objects.filter(image=instance)
        if thumbnails:
            response_dict["thumbnails"] = {}
            for thumbnail in thumbnails:
                response_dict["thumbnails"][f"{thumbnail.height}x{thumbnail.width}"] = request.build_absolute_uri(
                    reverse("images:serve_thumbnail", kwargs={"uuid": thumbnail.uuid})
                )

        return response_dict
