from rest_framework import viewsets
from .models import Loan  # Import your Loan model
from .serializers import LoanSerializer  # Ensure this import is correct

class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer