from rest_framework import viewsets
from .models import User  # or your user model
from .serializers import UserSerializer  # Ensure this import is correct

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer