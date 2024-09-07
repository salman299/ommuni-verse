# Standard library imports

from django.db.models import Q
from django.shortcuts import get_object_or_404

# Third-party imports
from rest_framework import status, viewsets, generics
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend


# Local imports
from app.community.models import (
    Community,
    CommunityJoinRequest,
    CommunityMembership,
)
from app.community.permissions import IsCommunityAdminOrManager
from app.community.api.v1.serializers import (
    CommunityJoinRequestSerializer,
    CommunityMembershipSerializer,
    ManageCommunityJoinRequestSerializer,
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
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["area__name", "area__city"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]
    ordering = ["created_at"]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["user"] = self.request.user
        return context

class UserCommunityListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Community.objects.filter(is_active=True, is_published=True)
    serializer_class = PublicCommunitySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["area__name", "area__city"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]
    ordering = ["created_at"]

    def get_queryset(self):
        community_memberships = CommunityMembership.objects.filter(
            user=self.request.user
        ).values_list("community", flat=True)
        communities = Community.objects.filter(id__in=community_memberships)
        return communities

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["user"] = self.request.user
        return context

class PublicCommunityDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Community.objects.filter(is_active=True, is_published=True)
    serializer_class = PublicCommunityDetailSerializer
    lookup_field = "slug"

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["user"] = self.request.user
        return context


class CommunityJoinView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Community.objects.filter(is_active=True, is_published=True)
    lookup_field = "slug"

    def create(self, request, *args, **kwargs):
        # Get the community slug from the URL
        community = self.get_object()

        # Check if the user has already requested to join the community
        if CommunityJoinRequest.objects.filter(
            community=community, user=request.user
        ).exists():
            return Response(
                {"detail": "You have already requested to join this community."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create the join request
        serializer = CommunityJoinRequestSerializer(
            data={"community": community.id}, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(), slug=self.kwargs[self.lookup_field]
        )

class ManageCommunityJoinRequestViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsCommunityAdminOrManager]
    serializer_class = ManageCommunityJoinRequestSerializer
    queryset = CommunityJoinRequest.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["community__slug", "status"]
    search_fields = ["user__profile__full_name"]
    ordering_fields = ["created_at", "community__name", "status"]
    ordering = ["created_at"]

    @action(detail=False, methods=['get'], url_path='communities')
    def list_communities(self, request):
        # Get all communities that the current user is a ower or manager of
        user = request.user
        community_ids = CommunityMembership.objects.filter(
            user=user, role__in=[CommunityMembership.OWNER, CommunityMembership.MANAGER]
        ).values_list('community_id', flat=True)
        communities = Community.objects.filter(id__in=community_ids).values('slug', 'name')
        return Response(communities, status=status.HTTP_200_OK)

    def get_queryset(self):
        user = self.request.user
        community_memberships = CommunityMembership.objects.filter(
            user=user, role__in=[CommunityMembership.OWNER, CommunityMembership.MANAGER]
        ).values_list("community", flat=True)

        join_requests = CommunityJoinRequest.objects.filter(community__in=community_memberships)
        return join_requests

class ManageCommunityViewSet(viewsets.ModelViewSet, AuditMixin):
    permission_classes = [IsAuthenticated, IsCommunityAdminOrManager]
    queryset = Community.objects.all()
    serializer_class = ManageCommunitySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["area", "area__city"]
    search_fields = ["name"]
    ordering_fields = ["name", "created_at"]
    ordering = ["created_at"]
    lookup_field = "slug"

    def get_queryset(self):
        user = self.request.user

        if user.is_staff or user.is_superuser:
            return self.queryset

        community_memberships = CommunityMembership.objects.filter(
            user=user, role__in=[CommunityMembership.OWNER, CommunityMembership.MANAGER]
        ).values_list("community", flat=True)

        communities = Community.objects.filter(id__in=community_memberships)

        return communities

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["user"] = self.request.user
        return context


class CommunityMembershipViewSet(viewsets.ModelViewSet, AuditMixin):
    queryset = CommunityMembership.objects.all()
    serializer_class = CommunityMembershipSerializer
    permission_classes = [IsAuthenticated, IsCommunityAdminOrManager]

    def get_queryset(self):
        community_slug = self.kwargs.get("slug")
        return self.queryset.filter(community__slug=community_slug)

    def perform_create(self, serializer):
        community_slug = self.kwargs.get("slug")
        community = get_object_or_404(Community, community__slug=community_slug)
        serializer.save(community=community)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.role == CommunityMembership.OWNER:
            return Response(
                {"error": "Cannot remove the owner"}, status=status.HTTP_400_BAD_REQUEST
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
