from __future__ import annotations

from django.contrib.auth import authenticate, password_validation
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import GenericAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from apps.months.models import ManagerAssignment, Month
from apps.users.models import User
from apps.users.permissions import HasCapability
from apps.users.serializers import (
    ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
    MeSerializer,
    UserCreateSerializer,
    UserDetailSerializer,
    UserListSerializer,
    UserPublicSerializer,
    generate_temporary_password,
)


class UserPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class CustomTokenObtainPairView:
    serializer_class = CustomTokenObtainPairSerializer


@api_view(["POST"])
@permission_classes([])
def login_view(request):
    serializer = CustomTokenObtainPairSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return Response(serializer.validated_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    refresh_token = request.data.get("refresh")
    if not refresh_token:
        return Response({"detail": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
    except TokenError:
        return Response({"detail": "Invalid or expired refresh token."}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"detail": "Logged out successfully."}, status=status.HTTP_200_OK)


class CustomTokenRefreshView(TokenRefreshView):
    pass


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me_view(request):
    serializer = MeSerializer(request.user)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response({"detail": "Password changed successfully."}, status=status.HTTP_200_OK)


class UserListCreateView(APIView):
    pagination_class = UserPagination
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        perms = super().get_permissions()
        if self.request.method == "GET":
            self.required_capability = "user.view"
        else:
            self.required_capability = "user.create"
        return [*perms, HasCapability()]

    def get(self, request, *args, **kwargs):
        queryset = User.objects.all().order_by("id")

        role = request.query_params.get("role")
        if role:
            queryset = queryset.filter(role=role)

        is_active = request.query_params.get("is_active")
        if is_active is not None:
            value = str(is_active).strip().lower()
            if value in {"true", "1", "yes"}:
                queryset = queryset.filter(is_active=True)
            elif value in {"false", "0", "no"}:
                queryset = queryset.filter(is_active=False)

        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(Q(username__icontains=search) | Q(email__icontains=search))

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        if page is not None:
            serializer = UserListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = UserListSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data["username"].strip()
        email = serializer.validated_data["email"].strip()

        if User.objects.filter(username__iexact=username).exists():
            return Response({"detail": "A user with this username already exists.", "code": "username_taken"}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email__iexact=email).exists():
            return Response({"detail": "A user with this email already exists.", "code": "email_taken"}, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        payload = UserDetailSerializer(user).data
        payload["temporary_password"] = getattr(user, "_temporary_password", "")
        return Response(payload, status=status.HTTP_201_CREATED)


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        perms = super().get_permissions()
        self.required_capability = "user.view"
        return [*perms, HasCapability()]

    def get(self, request, pk, *args, **kwargs):
        user = get_object_or_404(User, pk=pk)
        serializer = UserDetailSerializer(user)
        return Response(serializer.data)


class UserDeactivateView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        perms = super().get_permissions()
        self.required_capability = "user.deactivate"
        return [*perms, HasCapability()]

    def post(self, request, pk, *args, **kwargs):
        user = get_object_or_404(User, pk=pk)
        user.deactivate(actor=request.user)
        serializer = UserDetailSerializer(user)
        return Response(serializer.data)


class UserReactivateView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        perms = super().get_permissions()
        self.required_capability = "user.deactivate"
        return [*perms, HasCapability()]

    def post(self, request, pk, *args, **kwargs):
        user = get_object_or_404(User, pk=pk)
        user.is_active = True
        user.save(update_fields=["is_active"])
        serializer = UserDetailSerializer(user)
        return Response(serializer.data)


class UserResetPasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        perms = super().get_permissions()
        self.required_capability = "user.reset_password"
        return [*perms, HasCapability()]

    def post(self, request, pk, *args, **kwargs):
        user = get_object_or_404(User, pk=pk)
        temp_password = generate_temporary_password()
        password_validation.validate_password(temp_password, user=user)
        user.set_password(temp_password)
        user.must_change_password = True
        user.save(update_fields=["password", "must_change_password"])
        return Response({"id": user.id, "username": user.username, "temporary_password": temp_password})
