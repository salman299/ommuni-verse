"""
Root API URLs.
"""
from django.urls import path, include
from app.core.api.v1.views.login import RegisterView

app_name = 'v1_apis'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('', include('oauth2_provider.urls', namespace='oauth2_provider')),
    # other URL patterns
]
