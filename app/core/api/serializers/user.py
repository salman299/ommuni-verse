from rest_framework import serializers
from app.core.models import Person

class PersonSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Person
        fields = ['id', 'username', 'avatar', 'full_name', 'is_active']
