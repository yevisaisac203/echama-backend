# contributions/serializers.py
from rest_framework import serializers
from .models import Contribution
from groups.models import Group, Membership
from groups.serializers import MemberSummarySerializer


class ContributionSerializer(serializers.ModelSerializer):
    member = MemberSummarySerializer(read_only=True)

    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())

    class Meta:
        model = Contribution
        fields = ['id', 'member', 'group', 'amount', 'date']
        read_only_fields = ['id', 'member', 'date']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0.")
        return value

    def validate_group(self, value):
        request = self.context.get('request')
        if not Membership.objects.filter(group=value, user=request.user).exists():
            raise serializers.ValidationError("You must be a member of this group to record a contribution to it.")
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['member'] = request.user
        return super().create(validated_data)
