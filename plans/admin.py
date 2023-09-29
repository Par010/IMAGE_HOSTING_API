from django.contrib import admin

from .models import Plan, UserPlan


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("name", "include_original_link", "generate_expiring_links")
    list_filter = ("include_original_link", "generate_expiring_links")
    search_fields = ("name",)


@admin.register(UserPlan)
class UserPlanAdmin(admin.ModelAdmin):
    list_display = ("user", "plan")
    list_filter = ("user", "user")
    search_fields = ("user__email", "plan__name")
