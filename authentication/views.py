from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from authentication.models import User
from django.conf import settings
from django.contrib.auth import authenticate
import jwt

# Create your views here.


@api_view(["POST"])
def register(request):
    """
    register new user account
    """
    username = request.data.get("username")
    password = request.data.get("password")

    if username is None or password is None:
        return Response({
            "error": "username and password are required!"
        }, status=status.HTTP_400_BAD_REQUEST)

    existed = User.objects.filter(username=username).first()

    if existed:
        return Response({
            'error': "username has already been registered"
        }, status=status.HTTP_400_BAD_REQUEST)

    User.objects.create_user(username=username, password=password)

    return Response({
        'data': "created user {} successfully".format(username)
    }, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def login(request):
    """
    authenticate user account
    """
    username = request.data.get("username")
    password = request.data.get("password")

    if username is None or password is None:
        return Response({
            "error": "username and password are required!"
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        current_user = authenticate(username=username, password=password)
        if current_user is None:
            return Response({
                "error": "Authentication failed!"
            }, status=status.HTTP_400_BAD_REQUEST)

        request.user = current_user

        token = jwt.encode({
            "id": current_user.id,
            "username": current_user.username,
        },
            settings.SECRET_KEY,
            algorithm="HS256"
        )

        return Response({
            "token": token
        }, status=status.HTTP_200_OK)

    except BaseException:
        return Response({
            "error": "Unexpected error!"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
