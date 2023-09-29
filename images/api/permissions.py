from rest_framework import permissions

from plans.models import UserPlan


class CanAccessImageListViewSet(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user

        try:
            user_plan = UserPlan.objects.get(user=user)
        except UserPlan.DoesNotExist:
            return False

        if user_plan.plan.generate_expiring_links:
            return True

        return False
