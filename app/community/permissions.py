"""
Custom permissions
"""
from rest_framework import permissions

from app.community.models import CommunityMembership

class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to create it.
    """
    def has_object_permission(self, request, view, obj):
        community_slug = view.kwargs.get('slug')
        user = request.user
        membership = CommunityMembership.objects.filter(
            community__slug=community_slug,
            user=user,
            role=CommunityMembership.OWNER
        ).exists()
        return membership


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Get the community ID from the URL parameters
        community_id = view.kwargs.get('community_pk')

        # Check if the request method is safe (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True

        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return False

        # Check if the user is an owner of the community
        is_owner = CommunityMembership.objects.filter(
            community_id=community_id,
            user=request.user,
            role=CommunityMembership.OWNER
        ).exists()

        return is_owner

class IsOwnerOrManager(permissions.BasePermission):
    def has_permission(self, request, view):
        community_id = view.kwargs.get('community_pk')
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_staff or user.is_superuser:
            return True
        membership = CommunityMembership.objects.filter(
            community_id=community_id,
            user=user,
            role__in=[CommunityMembership.OWNER, CommunityMembership.MANAGER]
        ).exists()
        return membership


    def has_object_permission(self, request, view, obj):
        community_id = view.kwargs.get('community_pk')
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_staff or user.is_superuser:
            return True
        membership = CommunityMembership.objects.filter(
            community_id=community_id,
            user=user,
            role__in=[CommunityMembership.OWNER, CommunityMembership.MANAGER]
        ).exists()
        return membership
