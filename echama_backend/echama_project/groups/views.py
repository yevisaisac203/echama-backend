from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Group, Membership
from .permissions import IsGroupAdmin
from .serializers import AddMemberSerializer, GroupSerializer


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated, IsGroupAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == 'admin':
            return Group.objects.all()
        return Group.objects.filter(membership__user=user).distinct()

    def get_permissions(self):
        if self.action == 'leave':
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        group = self.get_object()
        serializer = AddMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        member = serializer.user
        if Membership.objects.filter(group=group, user=member).exists():
            return Response(
                {'detail': 'That user is already a member of this group.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        Membership.objects.create(group=group, user=member, is_admin=serializer.validated_data['is_admin'])
        return Response(GroupSerializer(group, context=self.get_serializer_context()).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def remove_member(self, request, pk=None):
        group = self.get_object()
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'detail': 'user_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        membership = Membership.objects.filter(group=group, user_id=user_id).first()
        if not membership:
            return Response({'detail': 'That user is not a member of this group.'}, status=status.HTTP_404_NOT_FOUND)

        if membership.is_admin and not Membership.objects.filter(group=group, is_admin=True).exclude(pk=membership.pk).exists():
            return Response({'detail': 'Cannot remove the only remaining admin.'}, status=status.HTTP_400_BAD_REQUEST)

        membership.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        group = get_object_or_404(self.get_queryset(), pk=pk)
        membership = Membership.objects.filter(group=group, user=request.user).first()
        if not membership:
            return Response({'detail': 'You are not a member of this group.'}, status=status.HTTP_400_BAD_REQUEST)

        other_members_exist = Membership.objects.filter(group=group).exclude(pk=membership.pk).exists()
        other_admin_exists = Membership.objects.filter(group=group, is_admin=True).exclude(pk=membership.pk).exists()
        if membership.is_admin and other_members_exist and not other_admin_exists:
            return Response(
                {'detail': 'Promote another member to admin before leaving.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        membership.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
