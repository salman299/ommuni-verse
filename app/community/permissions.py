"""
Custom permissions
"""

from rest_framework import permissions

from app.community.models import CommunityMembership


class IsCommunityAdminOrManager(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.is_staff or user.is_superuser:
            return True

        return obj.memberships.filter(
            user=user, role__in=[CommunityMembership.OWNER, CommunityMembership.MANAGER]
        ).exists()
