# Standard library imports
from django.db.models import Q
from django.shortcuts import get_object_or_404

# Third-party imports
from rest_framework import mixins, status, viewsets, generics, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend


# Local imports
from app.community.models import (
    Community,
    CommunityJoinRequest,
    CommunityMembership,
)
from app.community.permissions import IsCommunityAdminOrManager, IsOwnerOrManager
from app.community.api.v1.serializers import (
    CommunityJoinRequestSerializer,
    CommunityMembershipSerializer,
    ManageCommunitySerializer,
    PublicCommunityDetailSerializer,
    PublicCommunitySerializer,
)

class AuditMixin:
    """
    Audit Mixin
    """
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

class PublicCommunityListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Community.objects.filter(is_active=True, is_published=True)
    serializer_class = PublicCommunitySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['area__name', 'area__city']
    search_fields = ['name', 'description']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context

class PublicCommunityDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Community.objects.filter(is_active=True, is_published=True)
    serializer_class = PublicCommunityDetailSerializer
    lookup_field = 'slug'

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context

class ManageCommunityViewSet(viewsets.ModelViewSet, AuditMixin):
    permission_classes = [IsAuthenticated, IsCommunityAdminOrManager]
    queryset = Community.objects.all()
    serializer_class = ManageCommunitySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['area', 'area__city']
    search_fields = ['name']
    lookup_field = 'slug'

    def get_queryset(self):
        user = self.request.user
        
        if user.is_staff or user.is_superuser:
            return self.queryset

        community_memberships = CommunityMembership.objects.filter(
            user=user,
            role__in=[CommunityMembership.OWNER, CommunityMembership.MANAGER]
        ).values_list('community', flat=True)

        communities = Community.objects.filter(id__in=community_memberships)
        
        return communities

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context


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
