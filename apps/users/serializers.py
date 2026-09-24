from __future__ import annotations

from django.contrib.auth import password_validation
from django.contrib.auth.password_validation import validate_password
from django.utils.crypto import get_random_string
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.users.models import User


class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "must_change_password"]


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "phone",
            "is_active",
            "is_staff",
            "is_superuser",
            "date_joined",
        ]


class UserCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES)
    phone = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "role", "phone"]

    def validate_username(self, value):
        value = value.strip()
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def validate_email(self, value):
        value = value.strip()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        temp_password = generate_temporary_password()
        user = User(**validated_data, must_change_password=True, is_active=True)
        password_validation.validate_password(temp_password, user=user)
        user.set_password(temp_password)
        user.save()
        user._temporary_password = temp_password
        return user


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "phone",
            "is_active",
            "is_staff",
            "is_superuser",
            "must_change_password",
            "date_joined",
        ]
        read_only_fields = ["username", "role", "is_staff", "is_superuser", "must_change_password", "is_active", "date_joined"]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Emit role and manager hints in the token payload for UI convenience.

    IMPORTANT: these claims are UI hints only. Every server-side capability check must
    re-derive the current manager status live from the open month and ManagerAssignment.
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["is_manager"] = user.is_current_manager()
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserPublicSerializer(self.user).data
        return data


class MeSerializer(serializers.ModelSerializer):
    capabilities = serializers.SerializerMethodField()
    is_manager = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "role",
            "must_change_password",
            "is_manager",
            "capabilities",
        ]

    def get_capabilities(self, obj):
        return obj.current_capabilities()

    def get_is_manager(self, obj):
        return obj.is_current_manager()


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate(self, attrs):
        new_password = attrs.get("new_password")
        confirm_password = attrs.get("confirm_password")

        if new_password != confirm_password:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})

        validate_password(new_password, user=self.context["request"].user)
        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.must_change_password = False
        user.save(update_fields=["password", "must_change_password"])
        return user


def generate_temporary_password(length=18):
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+[]{};:,.<>/?"
    password = get_random_string(length, alphabet)
    if not any(ch.isupper() for ch in password):
        password = password[:-1] + "A"
    if not any(ch.islower() for ch in password):
        password = password[:-1] + "a"
    if not any(ch.isdigit() for ch in password):
        password = password[:-1] + "1"
    if not any(ch in "!@#$%^&*()-_=+[]{};:,.<>/?" for ch in password):
        password = password[:-1] + "!"
    return password
