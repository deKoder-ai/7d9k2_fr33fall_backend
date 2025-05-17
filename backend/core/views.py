# backend/core/views.py
from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import ExampleModel
from .serializers import ExampleModelSerializer
from users.models import CustomUser
from users.serializers import UserSerializer
from users.permissions import IsOwnerOrAdmin

class ExampleModelViewSet(viewsets.ModelViewSet):
    queryset = ExampleModel.objects.all()
    serializer_class = ExampleModelSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class CurrentUserView(generics.RetrieveAPIView):
    """
    View to get current authenticated user's information
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user