# backend/core/serializers.py
from rest_framework import serializers
from .models import ExampleModel

class ExampleModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExampleModel
        fields = ['id', 'name', 'description', 'owner', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'owner']