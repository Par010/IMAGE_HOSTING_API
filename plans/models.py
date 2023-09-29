import json

from django.core.exceptions import ValidationError
from django.db import models

from image_hosting_api.users.models import User


def validate_thumbnail_sizes(value):
    try:
        if not isinstance(value, list):
            raise ValueError("Invaild thumbnail_sizes input: must be a list of sizes")
        for size in value:
            if not isinstance(size, dict) or "height" not in size or "width" not in size:
                raise ValueError(
                    "Invaild thumbnail_sizes input: every thumbnail_sizes instance must have " "a height and width key"
                )
            height = size["height"]
            width = size["width"]
            if not isinstance(height, int) or not isinstance(width, int) or height <= 0 or width <= 0:
                raise ValueError(
                    "Invaild thumbnail_sizes input: thumbnail_sizes height and width must be positive integers"
                )
    except json.JSONDecodeError:
        raise ValidationError("Unable to decode JSON data")


class Plan(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False, unique=True)
    thumbnail_sizes = models.JSONField(
        default=list,
        validators=[validate_thumbnail_sizes],
        help_text="A list of dict, each containing 'height' and 'width' in integers for "
        "thumbnail sizes assumed to be in pixels",
    )
    include_original_link = models.BooleanField(default=False)
    generate_expiring_links = models.BooleanField(default=False)

    def __str__(self):
        return f"Plan - {self.name}"


class UserPlan(models.Model):
    user = models.OneToOneField(User, related_name="user_plan_user", on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, related_name="user_plan_plan", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "User Plan"
        verbose_name_plural = "User Plans"

    def __str__(self):
        return f"User Plan - {self.user.email} {self.plan.name}"
