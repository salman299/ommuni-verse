from django.contrib.auth import get_user_model
from rest_framework.response import Response

from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from app.core.api.serializers.login import RegisterSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    Registration View
    """
    permission_classes = (AllowAny,)
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
