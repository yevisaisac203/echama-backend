from rest_framework import mixins, permissions, viewsets

from .models import Contribution
from .permissions import IsGroupMember
from .serializers import ContributionSerializer


class ContributionViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Contributions are an append-only ledger: no update endpoint is exposed.
    Only a group admin (or staff) may delete an entry, to correct a mistake."""

    queryset = Contribution.objects.all()
    serializer_class = ContributionSerializer
    permission_classes = [permissions.IsAuthenticated, IsGroupMember]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == 'admin':
            return Contribution.objects.all()
        return Contribution.objects.filter(group__membership__user=user).distinct()
