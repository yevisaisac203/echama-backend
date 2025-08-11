from rest_framework import viewsets
from .models import Contribution  # or your contribution model
from .serializers import ContributionSerializer  # Ensure this import is correct

class ContributionViewSet(viewsets.ModelViewSet):
    queryset = Contribution.objects.all()
    serializer_class = ContributionSerializer