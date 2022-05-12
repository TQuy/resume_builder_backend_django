import json
from django.shortcuts import render, redirect
from django.db import IntegrityError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import User, Resume

# Create your views here.    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_resume(request):
    if request.method == 'GET':
        resume_list = request.user.resume_set.values('id', 'name')
        return Response(
            data = {
            'content': resume_list,
            'message': 'Loaded list of resumes successfully'
            }, 
            status = status.HTTP_200_OK,
        )
    else:
        return Response(
            data={
            'message': 'GET request required',
            }, 
            status=status.HTTP_400_BAD_REQUEST, 
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def load_resume(request, resume_id):
    if request.method == 'GET':
        # resume = get_object_or_404(Resume, pk=resume_id, user=request.user)
        try:
            resume = Resume.objects.get(pk=resume_id, user=request.user)
        except Resume.DoesNotExist:
            return Response({
                'message': 'Resume not found'
            }, status=status.HTTP_404_NOT_FOUND)
        return Response({
            'id': resume.id,
            'name': resume.name,
            'content': json.loads(resume.content),
            'message': 'Loaded resume successfully.'
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'message': 'GET request required'
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_resume(request):
    if request.method == 'POST':
        name = request.data['name']
        content = request.data['content']
        resume, _ = Resume.objects.get_or_create(user=request.user, name=name)
        resume.content = json.dumps(content)
        resume.save()
        return Response({
            'id': resume.id,
            'name': resume.name,
            'message': 'Saved resume successfully',
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'message': 'POST request required',
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_resume(request, resume_id):
    if request.method == 'DELETE':
        try:
            resume = Resume.objects.get(pk=resume_id, user=request.user)
        except Resume.DoesNotExist:
            return Response({
                'message': 'Resume not found'
            }, status=status.HTTP_404_NOT_FOUND)
        resume.delete()
        return Response({
            'message': 'Deleted resume successfully.'
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'message': 'DELETE request required.'
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def register_view(request):
    if request.method == 'POST':
        username = request.data['username']
        password = request.data['password']
        confirm_password = request.data['confirm_password']
        if password != confirm_password:
            Response({
                'message': 'Passwords must match.'
            }, status==status.HTTP_409_CONFLICT)
        try:
            user = User.objects.create_user(
                username=username,
                password=password
            )
            return Response({
                'message' 'Created new account successfully.'
            }, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({
                'message': 'This username is existed, please choose another one.'
            }, status=status.HTTP_406_NOT_ACCEPTABLE)
    else:
        return Response({
            'message': 'POST request required.'
        }, status=status.HTTP_400_BAD_REQUEST)
