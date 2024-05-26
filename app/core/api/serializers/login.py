"""
All Serializers are here
"""
import re
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from app.core.models import Person, Area


class UserSerializer(serializers.ModelSerializer):
    """
    Model Serializer to show details of all users
    """
    class Meta:
        """
        Model Meta Class
        """
        model = User
        fields = ['email', 'username']


class RegisterSerializer(UserSerializer):
    """
    Registration Serializer
    """
    full_name = serializers.CharField(write_only=True, required=True)
    area = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Area.objects.all())
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta(UserSerializer.Meta):
        """
        Model Meta class
        """
        fields = UserSerializer.Meta.fields + \
            ['full_name', 'area', 'password', 'confirm_password']

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError(
                {'password': "Password fields didn't match."})
        return super().validate(attrs)

    def validate_username(self, username):
        """
        Validate username
        """
        if not re.match(r"^[A-Za-z0-9]*$", username):
            raise serializers.ValidationError(
                'Username should only contain letters and numbers')
        return username

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')

        user = User.objects.create_user(
            username=validated_data.get('username'),
            email=validated_data.get('email'),
            password=password,
        )

        person_data = {
            'full_name': validated_data.pop('full_name'),
            'area': validated_data.pop('area'),
            'user': user
        }
        Person.objects.create(**person_data)

        return user
