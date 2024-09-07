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
    area_name = serializers.CharField(source="area.name", read_only=True)
    total_participants = serializers.SerializerMethodField(read_only=True)
    owner = serializers.SlugRelatedField(
        slug_field="username", queryset=User.objects.all(), write_only=True
    )

    class Meta:
        model = Community
        fields = [
            "id",
            "slug",
            "name",
            "description",
            "is_published",
            "is_active",
            "area",
            "area_name",
            "logo",
            "cover_image",
            "color",
            "total_participants",
            "owner",
            "created_at",
        ]
        read_only_fields = ("id", "is_active", "total_participants", "created_at")

    def get_owner(self, obj):
        return obj.memberships.filter(role=CommunityMembership.OWNER).first()

    def get_total_participants(self, obj):
        return obj.memberships.count()

    def validate_slug(self, value):
        if not re.match(r"^[a-z-]+$", value):
            raise ValidationError("Slug can only contain lowercase letters and dashes.")
        return value

    def create(self, validated_data):
        owner = validated_data.pop("owner")
        validated_data['created_by'] = self.context["user"]
        community = Community.objects.create(**validated_data)
        CommunityDetail.objects.create(community=community)
        CommunityMembership.objects.get_or_create(
            community=community, user=owner, role=CommunityMembership.OWNER
        )
        return community
    
    def update(self, instance, validated_data):
        validated_data['updated_by'] = self.context["user"]
        return super().update(instance, validated_data)

class PublicCommunitySerializer(serializers.ModelSerializer):
    is_member = serializers.SerializerMethodField()
    join_status = serializers.SerializerMethodField()
    area_name = serializers.CharField(source="area.name", read_only=True)

    class Meta:
        model = Community
        fields = [
            "id",
            "slug",
            "name",
            "description",
            "is_published",
            "area_name",
            "logo",
            "cover_image",
            "color",
            "is_member",
            "join_status",
        ]

    def get_is_member(self, obj):
        user = self.context["user"]
        return obj.memberships.filter(user=user).exists()

    def get_join_status(self, obj):
        user = self.context["user"]
        if join_request := obj.join_requests.filter(user=user).first():
            return join_request.status
        return None


class PublicCommunityDetailSerializer(serializers.ModelSerializer):
    is_member = serializers.SerializerMethodField()
    area_name = serializers.CharField(source="area.name", read_only=True)
    total_participants = serializers.SerializerMethodField()

    class Meta:
        model = Community
        fields = [
            "id",
            "slug",
            "name",
            "description",
            "is_published",
            "area_name",
            "logo",
            "cover_image",
            "color",
            "is_member",
            "total_participants",
        ]

    def get_is_member(self, obj):
        user = self.context["user"]
        return obj.memberships.filter(user=user).exists()

    def get_total_participants(self, obj):
        return obj.memberships.count()


class CommunityMembershipSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field="username", queryset=User.objects.all()
    )

    class Meta:
        model = CommunityMembership
        fields = ("user", "role")

    def validate_role(self, value):
        if (
            value == CommunityMembership.OWNER
            and self.instance
            and self.instance.role == CommunityMembership.OWNER
        ):
            raise serializers.ValidationError("Cannot change the role of the owner.")
        return value


class CommunityJoinRequestSerializer(serializers.ModelSerializer):
    username = serializers.SlugRelatedField(
        slug_field="user__username",
        read_only=True,
    )
    communtiy_slug = serializers.SlugRelatedField(
        slug_field="community__slug",
        read_only=True,
    )

    class Meta:
        model = CommunityJoinRequest
        fields = ("community", "status", "username", "communtiy_slug", "created_at")
        read_only_fields = ("username", "status", "communtiy_slug", "created_at")
        write_only_fields = "community"

    def create(self, validated_data):
        # Automatically set the user from the request
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class ManageCommunityJoinRequestSerializer(serializers.ModelSerializer):
    user_full_name = serializers.CharField(source="user.profile.full_name", read_only=True)
    community_name = serializers.CharField(source="community.name", read_only=True)

    class Meta:
        model = CommunityJoinRequest
        fields = (
            "id",
            "community",
            "status",
            "user",
            "user_full_name",
            "community_name",
            "created_at",
            "updated_at",
            "updated_by",
        )
        read_only_fields = ("user", "community", )
        write_only_fields = ("status",)

    def update(self, instance, validated_data):
        validated_data["updated_by"] = self.context["request"].user
        status = validated_data.get('status', instance.status)

        if instance.status == CommunityJoinRequest.PENDING and status == CommunityJoinRequest.APPROVED:
            # Create CommunityMembership instance
            CommunityMembership.objects.get_or_create(
                user=instance.user,
                community=instance.community,
                defaults={'role': CommunityMembership.MEMBER}
            )
        return super().update(instance, validated_data)
