from django.contrib import admin

from .models import Image, Thumbnail


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "image", "upload_time")
    list_filter = ("user",)
    search_fields = ("name", "user__email")
    readonly_fields = ("uuid",)


@admin.register(Thumbnail)
class ThumbnailAdmin(admin.ModelAdmin):
    list_display = ("image", "height", "width", "thumbnail")
    list_filter = ("image",)
    search_fields = ("image__title",)
    readonly_fields = ("image", "height", "width", "thumbnail", "uuid")
