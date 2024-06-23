# serializers.py
from rest_framework import serializers
from app.core.models import Area

class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ['id', 'name', 'city', 'council', 'region']
