from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAdminUser
from app.core.models import Person
from app.core.api.serializers.user import PersonSerializer

class PersonListView(ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = PersonSerializer
    filter_backends = [SearchFilter]
    search_fields = ['full_name', 'user__username']
    queryset = Person.objects.all()
