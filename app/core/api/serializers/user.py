from rest_framework import serializers
from app.core.models import Person


class PersonSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Person
        fields = ["id", "username", "avatar", "full_name", "is_active"]


class UserDetailUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = [
            "full_name",
            "fathers_name",
            "personal_email",
            "date_of_birth",
            "nic",
            "gender",
            "marital_status",
            "cellphone_number",
            "whatsapp_cellphone_number",
            "emergency_contact_name",
            "emergency_contact_number",
            "current_address",
            "permanent_address",
            "city",
            "person_id",
            "avatar",
            "thumbnail",
            "is_active",
            "created_at",
            "modified_at",
            "emergency_contact_relation",
            "area",
        ]
        read_only_fields = ["created_at", "modified_at", "person_id"]
