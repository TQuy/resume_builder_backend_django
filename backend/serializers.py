from backend.models import Resume
from rest_framework import serializers
import json


class ResumeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Resume
        fields = ["id", "name", "content"]

    def to_representation(self, instance):
        """Convert `username` to lowercase."""
        ret = super().to_representation(instance)
        ret["content"] = json.loads(ret["content"])
        return ret
