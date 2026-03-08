from django.contrib.auth import get_user_model
from rest_framework import serializers

from core.validators import validate_language

User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    language = serializers.CharField(max_length=2, default="en", required=False)

    class Meta:
        model = User
        fields = ("email", "password", "language")

    def validate_email(self, value):
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()

    def validate_language(self, value):
        validate_language(value)
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "language", "is_premium", "created_at")
        read_only_fields = ("id", "email", "is_premium", "created_at")
