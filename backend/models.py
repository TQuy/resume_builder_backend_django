from django.db import models
from authentication.models import User


class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add=True)
    modified_at = models.DateField(auto_now=True)
    name = models.CharField(max_length=100)
    content = models.TextField(blank=True, max_length=1000)

    def __str__(self):
        return f"{self.id} - {self.name}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'name',
                    'user'],
                name='unique_resume_name')
        ]
