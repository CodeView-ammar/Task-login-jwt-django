from rest_framework import serializers
from rest_framework import viewsets, status
from .models import User
from email.policy import default
from rest_framework import permissions

from .models import User
from rest_framework.decorators import action
from rest_framework.response import Response

from user.mail import send_verify_email
from django.http import HttpResponseRedirect
from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager

import logging


# This code defines a Django REST framework serializer for the User model.

class UserSerializer(serializers.ModelSerializer):

    # The `exclude` attribute specifies the fields that should be excluded from the serializer.
    class Meta:
        model = User
        exclude = ['password', 'email_code']


# This code defines a Django REST framework serializer for updating a user.

class UpdateUserSerializer(serializers.ModelSerializer):

    # The `exclude` attribute specifies the fields that should be excluded from the serializer.
    class Meta:
        model = User
        exclude = ['password', 'is_admin', 'is_active', 'email_verified', 'email_code']

    def to_representation(self, instance):
        # This method returns the representation of the user.
        return UserSerializer(instance=instance).data


# This code defines a Django REST framework serializer for creating a user.

class CreateUserSerializer(serializers.ModelSerializer):

    # The `exclude` attribute specifies the fields that should be excluded from the serializer.
    class Meta:
        model = User
        exclude = ['email_code']

        # The `extra_kwargs` attribute specifies the additional keyword arguments that should be passed to the serializer.
        extra_kwargs = {
            'is_admin': {'read_only': True},
            'is_active': {'read_only': True},
            'last_login': {'read_only': True},
            'email_verified': {'read_only': True},
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        # This method creates a new user and returns the user object.
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def to_representation(self, instance):
        # This method returns the representation of the user.
        return UserSerializer(instance=instance).data


# This code defines a Django REST framework serializer for resetting a user's password.

class ResetPasswordSerializer(serializers.ModelSerializer):

    # The `fields` attribute specifies the fields that should be included in the serializer.
    class Meta:
        model = User
        fields = ['password']


# This code defines a custom permission class that allows only the user or an administrator to update their own account.

class IsAdminOrIsSelf(permissions.IsAuthenticated):

    def has_object_permission(self, request, view, obj):
        # This method checks if the user is allowed to update the object.
        return obj.id == request.user.id or request.user.is_admin


# This code defines a Django REST framework viewset for handling user requests.

class UserViewSet(viewsets.ModelViewSet):

    # The `queryset` attribute specifies the queryset for the viewset.
    queryset = User.objects.all().order_by('-date_joined')

    # The `serializer_class` attribute specifies the serializer class for the viewset.
    serializer_class = UserSerializer

    # The `http_method_names` attribute specifies the HTTP methods that the viewset supports.
    http_method_names = ['get', 'post', 'put']

    # The `get_permissions` method returns the permissions that are required to access the viewset.
    def get_permissions(self):
        # This method returns the permissions that are required to access the viewset.
        match self.action:
            case 'create':
                permission_classes = []
            case 'delete':
                permission_classes = [permissions.IsAdminUser]
            case 'update':
                permission_classes = [IsAdminOrIsSelf]
            case 'reset_password':
                permission_classes = [IsAdminOrIsSelf]
            case 'send_verify_email':
                permission_classes = [IsAdminOrIsSelf]
            case 'verify_email':
                permission_classes = []
        return [permission() for permission in permission_classes]
@action(methods=['post'], detail=False, url_path='send-verify-email')
def send_verify_email(self, request):

    # This method sends a verification email to the user.

    user = request.user
    user.email_code = BaseUserManager().make_random_password(length=50)
    user.save()
    link = settings.SERVER_HOST + '/api/user/' + f'{user.id}/verify-email/?email_code={user.email_code}'
    send_verify_email(request.user, link)
    return Response({'msg': f'Verification Email has been sent to {user.email}'})


def get_serializer_class(self):

    # This method returns the serializer class that should be used for the current action.

    match self.action:
        case 'create':
            return CreateUserSerializer
        case 'update':
            return UpdateUserSerializer
        case 'reset_password':
            return ResetPasswordSerializer
        case 'verify_email':
            return None
        case 'send_verify_email':
            return None
        case _:
            return UserSerializer


@action(methods=['post'], detail=True, url_path='reset-password')
def reset_password(self, request, *args, **kwargs):

    # This method resets the password for the user.

    password = request.data.pop('password')
    user = self.get_object()
    user.set_password(password)
    user.save()
    return Response({'status': True})