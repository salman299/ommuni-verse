from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter
from app.community.api.v1.views import (
    CommunityViewSet,
    CommunityMembershipViewSet,
    CommunityJoinRequestViewSet,
)
app_name = 'commmunity_apis'

api_v1_router = DefaultRouter()
api_v1_router.register('communities', CommunityViewSet, basename='community')
api_v1_router.register('communities/<slug:slug>/members', CommunityMembershipViewSet, basename='community-membership')
api_v1_router.register('communities/<slug:slug>/join-requests', CommunityJoinRequestViewSet, basename='community-join-request')

urlpatterns = [
    url('v1/', include(api_v1_router.urls)),
]
