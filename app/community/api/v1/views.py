# Standard library imports
from django.db.models import Q
from django.shortcuts import get_object_or_404

# Third-party imports
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

# Local imports
from app.community.models import (
    Community,
    CommunityJoinRequest,
    CommunityMembership,
)
from app.community.permissions import IsOwner, IsOwnerOrManager, IsOwnerOrReadOnly
from app.community.api.v1.serializers import (
    CommunityJoinRequestSerializer,
    CommunityMembershipSerializer,
    CommunitySerializer,
)

class AuditMixin:
    """
    Audit Mixin
    """
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class CommunityViewSet(AuditMixin, viewsets.ModelViewSet):
    """
    create/update: Only allow admins to create amd update communities
    retreive: Get community by slug
    create: Only allow Admins to create the community
    update: Allow admins or admin managers to update the community
    list: List of all communities accessible to the authenticated user
    public: List of active and published comminities.
    """
    queryset = Community.objects.all()
    serializer_class = CommunitySerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsAuthenticated, IsAdminUser]
        elif self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsAuthenticated, IsOwnerOrManager]
        elif self.action == 'list':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]


    def get_queryset(self):
        user = self.request.user

        if user.is_staff or user.is_superuser:
            return self.queryset

        user_memberships = CommunityMembership.objects.filter(user=user)
        managed_communities = user_memberships.filter(
            role__in=[CommunityMembership.OWNER, CommunityMembership.MANAGER]
        ).values_list('community', flat=True)

        member_communities = user_memberships.filter(
            role=CommunityMembership.MEMBER
        ).values_list('community', flat=True)

        return self.queryset.filter(
            Q(id__in=managed_communities) |
            Q(id__in=member_communities)
        ).distinct()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permission() for permission in [IsAuthenticated, IsOwnerOrReadOnly]]
        elif self.action in ['update', 'partial_update']:
            return [permission() for permission in [IsOwner]]
        return super().get_permissions()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        search_term = request.query_params.get('search', None)
        if search_term:
            queryset = queryset.filter(name__icontains=search_term)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def public(self, request, *args, **kwargs):
        """
        Retrieve a list of active and public communities.
        """
        queryset = self.queryset.filter(is_active=True, is_published=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['create'])
    def add_members(self, request, *args, **kwargs):
        """
        Allow Admin to add memebers in the community
        """


class CommunityMembershipViewSet(mixins.ListModelMixin,
                                 mixins.CreateModelMixin,
                                 mixins.DestroyModelMixin,
                                 viewsets.GenericViewSet):
    queryset = CommunityMembership.objects.all()
    serializer_class = CommunityMembershipSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrManager]
    lookup_field = 'slug'

    def get_queryset(self):
        community_slug = self.kwargs.get('slug')
        return self.queryset.filter(slug=community_slug)

    def perform_create(self, serializer):
        community_slug = self.kwargs.get('slug')
        community = get_object_or_404(Community, slug=community_slug)
        serializer.save(community=community)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.role == CommunityMembership.OWNER:
            return Response({"error": "Cannot remove the owner"}, status=status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

class CommunityJoinRequestViewSet(mixins.CreateModelMixin,
                                  mixins.ListModelMixin,
                                  mixins.UpdateModelMixin,
                                  viewsets.GenericViewSet):
    queryset = CommunityJoinRequest.objects.all()
    serializer_class = CommunityJoinRequestSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'

    def get_queryset(self):
        community_id = self.kwargs.get('slug')
        return self.queryset.filter(community_id=community_id)

    def perform_create(self, serializer):
        community_slug = self.kwargs.get('slug')
        community = get_object_or_404(Community, slug=community_slug)
        serializer.save(community=community, user=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.approved:
            return Response({"error": "Request already approved"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def get_permissions(self):
        if self.action == 'create':
            return [permission() for permission in self.permission_classes]
        elif self.action in ['list', 'update']:
            return [IsOwnerOrManager()]
        return super().get_permissions()
