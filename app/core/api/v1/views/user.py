from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    RetrieveUpdateAPIView,
)
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from app.core.api.serializers.user import UserDetailUpdateSerializer
from app.core.models import Person
from app.core.api.serializers.user import PersonSerializer


class PersonListView(ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = PersonSerializer
    filter_backends = [SearchFilter]
    search_fields = ["full_name", "user__username"]
    queryset = Person.objects.all()


class PersonRetrieveView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PersonSerializer

    def get_object(self):
        return self.request.user.person


class UserRetrieveUpdateView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserDetailUpdateSerializer

    def get_object(self):
        person = Person.objects.get(id=self.request.user.id)
        return person
