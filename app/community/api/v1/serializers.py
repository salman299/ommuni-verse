import re
from django.forms import ValidationError
from rest_framework import serializers
from django.contrib.auth import get_user_model
from app.community.models import (
    Community,
    CommunityDetail,
    CommunityMembership,
    CommunityJoinRequest,
)

User = get_user_model()

class ManageCommunitySerializer(serializers.ModelSerializer):
    area_name = serializers.CharField(source='area.name', read_only=True)
    total_participants = serializers.SerializerMethodField(read_only=True)
    owner = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all(), write_only=True)

    class Meta:
        model = Community
        fields = ['id', 'slug', 'name', 'description', 'is_published', 'is_active', 'area', 
                  'area_name', 'logo', 'cover_image', 'color', 
                  'total_participants', 'owner', 'created_at']
        read_only_fields = ('id', 'is_active', 'total_participants', 'created_at')

    def get_owner(self, obj):
        return obj.memberships.filter(role=CommunityMembership.OWNER).first()

    def get_total_participants(self, obj):
        return obj.memberships.count()
    
    def validate_slug(self, value):
        if not re.match(r'^[a-z-]+$', value):
            raise ValidationError("Slug can only contain lowercase letters and dashes.")
        return value
    
    def create(self, validated_data):
        owner = validated_data.pop('owner')
        community = Community.objects.create(**validated_data)
        CommunityDetail.objects.create(community=community)
        CommunityMembership.objects.get_or_create(community=community, user=owner, role=CommunityMembership.OWNER)
        return community

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.is_published = validated_data.get('is_published', instance.is_published)
        instance.area = validated_data.get('area', instance.area)
        instance.save()
        return instance


class PublicCommunitySerializer(serializers.ModelSerializer):
    is_member = serializers.SerializerMethodField()
    area_name = serializers.CharField(source='area.name', read_only=True)

    class Meta:
        model = Community
        fields = ['id', 'slug', 'name', 'description', 'is_published', 
                  'area_name', 'logo', 'cover_image', 'color', 'is_member']

    def get_is_member(self, obj):
        user = self.context['user']
        return obj.memberships.filter(user=user).exists()

class PublicCommunityDetailSerializer(serializers.ModelSerializer):
    is_member = serializers.SerializerMethodField()
    area_name = serializers.CharField(source='area.name', read_only=True)
    total_participants = serializers.SerializerMethodField()

    class Meta:
        model = Community
        fields = ['id', 'slug', 'name', 'description', 'is_published', 
                  'area_name', 'logo', 'cover_image', 'color', 'is_member',
                  'total_participants']

    def get_is_member(self, obj):
        user = self.context['user']
        return obj.memberships.filter(user=user).exists()

    def get_total_participants(self, obj):
        return obj.memberships.count()


class CommunityMembershipSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )
    class Meta:
        model = CommunityMembership
        fields = ('user', 'role')

    def validate_role(self, value):
        if value == CommunityMembership.OWNER and self.instance and self.instance.role == CommunityMembership.OWNER:
            raise serializers.ValidationError("Cannot change the role of the owner.")
        return value

class CommunityJoinRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityJoinRequest
        fields = ('user', 'status', 'community__slug')
        read_only_fields = ('status',)

    def create(self, validated_data):
        # Automatically set the user from the request
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    

