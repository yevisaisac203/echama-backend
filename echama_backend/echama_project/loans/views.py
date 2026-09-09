from django.utils import timezone
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Loan
from .permissions import IsGroupAdminForDecision, IsGroupMember
from .serializers import LoanSerializer


class LoanViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Loan requests are immutable once submitted: status changes only happen
    through the approve/decline actions, which are restricted to that group's
    admins. A member may withdraw (delete) their own request while it's still
    pending; a decided loan is a permanent record."""

    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated, IsGroupMember]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == 'admin':
            return Loan.objects.all()
        return Loan.objects.filter(group__membership__user=user).distinct()

    def get_permissions(self):
        if self.action in ('approve', 'decline'):
            return [permissions.IsAuthenticated(), IsGroupAdminForDecision()]
        return super().get_permissions()

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        loan = self.get_object()
        if loan.status != 'pending':
            return Response({'detail': 'Only a pending loan can be approved.'}, status=status.HTTP_400_BAD_REQUEST)
        loan.status = 'approved'
        loan.approved_on = timezone.now()
        loan.save(update_fields=['status', 'approved_on'])
        return Response(LoanSerializer(loan, context=self.get_serializer_context()).data)

    @action(detail=True, methods=['post'])
    def decline(self, request, pk=None):
        loan = self.get_object()
        if loan.status != 'pending':
            return Response({'detail': 'Only a pending loan can be declined.'}, status=status.HTTP_400_BAD_REQUEST)
        loan.status = 'declined'
        loan.save(update_fields=['status'])
        return Response(LoanSerializer(loan, context=self.get_serializer_context()).data)
