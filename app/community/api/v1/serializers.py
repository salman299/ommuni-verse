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
from app.core.api.serializers.area import AreaSerializer

User = get_user_model()

class CommunityUserSerializer(serializers.ModelSerializer):
    class Meta:
        model =  User
        fields = ("username", )

class CommunityDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityDetail
        fields = ('additional_info', 'rules', 'community',)
        read_only_fields = ('community',)

class CommunitySerializer(serializers.ModelSerializer):
    area_details = AreaSerializer(source='area', read_only=True)

    owner = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
        write_only=True
    )

    class Meta:
        model = Community
        fields = (
            'slug', 'name', 'description', 'is_published', 'is_active', 'area',
            'area_details', 'owner', 'color', 'logo', 'cover_image',
        )
        write_only_fields = ('name', 'description', 'area', 'is_published', 'slug', 'color', 'logo', 'cover_image')
        extra_kwargs = {'area': {'required': True}} 

    def get_owner(self, object):
        """
        Get the owner of the community.
        """
        return CommunityMembership.objects.filter(role=CommunityMembership.OWNER).first()

    def validate_slug(self, value):
        # Check if slug contains only lowercase alphabets and dashes
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


class UserCommunities(serializers.ModelSerializer):
    details = CommunityDetailSerializer(write_only=True)
    
    class Meta:
        model = Community
        fields = '__all__'

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
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    
    class Meta:
        model = CommunityJoinRequest
        fields = ('user', 'status')
        read_only_fields = ('status',)

    def validate(self, attrs):
        community = self.context['view'].kwargs.get('community_pk')
        user = self.context['request'].user
        if CommunityMembership.objects.filter(community_id=community, user=user).exists():
            raise serializers.ValidationError("You are already a member of this community.")
        if CommunityJoinRequest.objects.filter(community_id=community, user=user).exists():
            raise serializers.ValidationError("You have already requested to join this community.")
        return attrs
