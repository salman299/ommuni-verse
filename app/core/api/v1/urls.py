"""
Root API URLs.
"""
from django.urls import path, include
from app.core.api.v1.views.login import RegisterView
from app.core.api.v1.views.area import AreaListView, UniqueCitiesView
from app.core.api.v1.views.user import PersonListView, PersonRetrieveView

app_name = 'v1_apis'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('areas/', AreaListView.as_view(), name='area'),
    path('areas-cities/', UniqueCitiesView.as_view(), name='area-cities'),
    path('users/', PersonListView.as_view(), name='users'),
    path('current-user/', PersonRetrieveView.as_view(), name='current-user'),
    path('', include('oauth2_provider.urls', namespace='oauth2_provider')),
    # other URL patterns
]
