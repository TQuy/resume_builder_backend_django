import json
from django.shortcuts import render, redirect
from django.db import IntegrityError
from rest_framework import status
from authentication.decorators import token_required
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import User, Resume
from backend.serializers import ResumeSerializer

# Create your views here.


@token_required
@api_view(['GET', 'PUT'])
def resumes(request, current_user):
    if request.method == 'GET':
        # list resumes of current user
        resumes = current_user.resume_set.values('id', 'name')
        return Response({
            "resumes": resumes
        }, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        # update or create current user's resume
        name = request.data['name']
        content = request.data['content']

        if name is None or content is None:
            return Response({
                "error": "name and content of resume are required!"
            }, status=status.HTTP_400_BAD_REQUEST)

        resume, created = Resume.objects.update_or_create(
            user=current_user, name=name, defaults={
                "content": content})

        resume_json = ResumeSerializer(resume)

        if created:
            return Response({
                "resume": resume_json.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            "resume": resume_json.data,
        }, status=status.HTTP_200_OK)


@token_required
@api_view(['GET', 'DELETE'])
def resume(request, current_user, resume_id):
    if request.method == 'GET':
        resume = current_user.resume_set.filter(pk=resume_id).first()

        if resume is None:
            return Response({
                'error': 'resume not found!'
            }, status=status.HTTP_404_NOT_FOUND)

        resume_json = ResumeSerializer(resume)
        return Response({
            'resume': resume_json.data
        }, status=status.HTTP_200_OK)

    if request.method == "DELETE":
        count, _ = current_user.resume_set.filter(pk=resume_id).delete()

        if count == 0:
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({
            "data": "OK"
        }, status=status.HTTP_200_OK)
