from backend.models import Resume
from rest_framework import serializers


class ResumeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Resume
        fields = ["id", "name", "content"]
