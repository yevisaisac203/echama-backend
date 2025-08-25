# groups/serializers.py
from rest_framework import serializers
from .models import Group, Membership
from users.serializers import UserSerializer

class MembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Membership
        fields = ['id', 'user', 'joined_on', 'is_admin']
        read_only_fields = ['id', 'user', 'joined_on', 'is_admin']  # membership creation handled by server

class GroupSerializer(serializers.ModelSerializer):
    
    members = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ['id', 'name', 'description', 'created_by', 'created_at', 'members']
        read_only_fields = ['id', 'created_by', 'created_at']

    def get_members(self, obj):
        """
        SerializerMethodField method: returns a serialized list of members.
        We query Membership and reuse MembershipSerializer.
        """
        qs = Membership.objects.filter(group=obj).select_related('user')
        return MembershipSerializer(qs, many=True).data

    def create(self, validated_data):
        """
        When a user creates a group:
         - set created_by to request.user
         - create the group
         - create a Membership linking the creator as admin
        The request is available at self.context['request'] (DRF passes this automatically when using ViewSets).
        """
        request = self.context.get('request')
        group = Group.objects.create(created_by=request.user, **validated_data)
        Membership.objects.create(user=request.user, group=group, is_admin=True)
        return group
