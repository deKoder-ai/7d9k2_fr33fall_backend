# backend/core/models.py
from django.db import models
from users.models import CustomUser

class BaseModel(models.Model):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class ExampleModel(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField()
    
    def __str__(self):
        return self.name