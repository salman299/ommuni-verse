from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app.community.api.v1.views import (
    ManageCommunityViewSet,
    CommunityMembershipViewSet,
    CommunityJoinRequestViewSet,
    PublicCommunityDetailView,
    PublicCommunityListView,
)
app_name = 'commmunity_apis'

api_v1_router = DefaultRouter()
api_v1_router.register('communities', ManageCommunityViewSet, basename='manage-community')
api_v1_router.register(r'communities/(?P<slug>[^/.]+)/members', CommunityMembershipViewSet, basename='community-membership')
api_v1_router.register(r'communities/(?P<slug>[^/.]+)/join-requests', CommunityJoinRequestViewSet, basename='community-join-request')


urlpatterns = [
    path('v1/', include(api_v1_router.urls)),
    path('v1/public/communities/', PublicCommunityListView.as_view(), name='public-community-list'),
    path('v1/public/communities/<slug:slug>/', PublicCommunityDetailView.as_view(), name='public-community-detail'),
]
