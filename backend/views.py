from django.shortcuts import render, redirect
from django.db.models import QuerySet
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from authentication.decorators import token_required
from backend.models import Resume
from authentication.models import User
from backend.serializers import ResumeSerializer

# Create your views here.


@token_required
@api_view(['GET', 'PUT', 'DELETE'])
def resumes(request, current_user: User) -> Response:
    """GET resumes or PUT resume"""
    if request.method == 'GET':
        # list resumes of current user
        resumes: QuerySet = current_user.resume_set.all()

        return Response({
            "resumes": ResumeSerializer(resumes, many=True).data
        }, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        # update or create current user's resume
        name = request.data.get('name')
        content = request.data.get('content')

        if name is None or content is None:
            return Response({
                "error": "name and content of resume are required!"
            }, status=status.HTTP_400_BAD_REQUEST)

        resume, created = Resume.objects.update_or_create(
            user=current_user, name=name, defaults={
                "content": content})

        if created:
            return Response({
                "message": "Resume saved successfully."
            }, status=status.HTTP_201_CREATED)

        return Response({
            "resume": "Error happened, save unsuccessfully.",
        }, status=status.HTTP_200_OK)

    if request.method == "DELETE":
        resume_name = request.data.get('name')

        if resume_name is None:
            return Response({
                "error": "resume_name not found"
            }, status=status.HTTP_400_BAD_REQUEST)

        count, _ = current_user.resume_set.filter(name=resume_name).delete()

        if count == 0:
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({
            "message": "OK"
        }, status=status.HTTP_200_OK)


@token_required
@api_view(['GET'])
def resume(request, current_user: User, resume_name: str) -> Response:
    if request.method == 'GET':
        resume = current_user.resume_set.filter(name=resume_name).first()

        if resume is None:
            return Response({
                'error': 'resume not found!'
            }, status=status.HTTP_404_NOT_FOUND)

        resume_json = ResumeSerializer(resume)
        return Response({
            'resume': resume_json.data
        }, status=status.HTTP_200_OK)
