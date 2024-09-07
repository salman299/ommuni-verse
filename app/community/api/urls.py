from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app.community.api.v1.views import (
    ManageCommunityViewSet,
    CommunityMembershipViewSet,
    ManageCommunityJoinRequestViewSet,
    PublicCommunityDetailView,
    PublicCommunityListView,
    CommunityJoinView,
    UserCommunityListView
)
app_name = 'commmunity_apis'

api_v1_router = DefaultRouter()
api_v1_router.register('communities', ManageCommunityViewSet, basename='manage-community')
api_v1_router.register('community-join-requests', ManageCommunityJoinRequestViewSet, basename='manage-community-join-requests')
api_v1_router.register(r'communities/(?P<slug>[^/.]+)/members', CommunityMembershipViewSet, basename='community-membership')

urlpatterns = [
    path('v1/', include(api_v1_router.urls)),
    path('v1/public/communities/', PublicCommunityListView.as_view(), name='public-community-list'),
    path('v1/public/communities/<slug:slug>/', PublicCommunityDetailView.as_view(), name='public-community-detail'),
    path('v1/public/communities/<slug:slug>/join', CommunityJoinView.as_view(), name='public-join-communty'),
    path('v1/my-communities/', UserCommunityListView.as_view(), name='my-community-list'),
    # path('v1/community-join-requests/', ManageCommunityJoinView.as_view(), name='manage-community-join-request-list'),
    # path('v1/community-join-requests/<int:pk>', ManageCommunityJoinView.as_view(), name='manage-community-join-request-detail'),
]
