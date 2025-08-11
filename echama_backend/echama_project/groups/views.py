from rest_framework import viewsets
from .models import Group  # or your group model
from .serializers import GroupSerializer  # Ensure this import is correct

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer