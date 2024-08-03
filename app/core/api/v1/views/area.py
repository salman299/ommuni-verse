# views.py
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from app.core.models import Area
from app.core.api.serializers.area import AreaSerializer

class AreaListView(generics.ListAPIView):
    pagination_class = None
    serializer_class = AreaSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        queryset = Area.objects.all()
        city = self.request.query_params.get('city', None)
        if city is not None:
            queryset = queryset.filter(city__iexact=city)
        return queryset

class UniqueCitiesView(generics.ListAPIView):
    pagination_class = None
    permission_classes = (AllowAny, )

    def list(self, request):
        cities = Area.objects.values_list('city', flat=True).distinct().order_by('city')
        return Response(cities)
