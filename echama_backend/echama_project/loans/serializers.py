# loans/serializers.py
from decimal import Decimal

from django.db.models import Sum
from rest_framework import serializers

from .models import Loan
from contributions.models import Contribution
from groups.models import Group, Membership
from groups.serializers import MemberSummarySerializer


class LoanSerializer(serializers.ModelSerializer):
    member = MemberSummarySerializer(read_only=True)
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())

    class Meta:
        model = Loan
        fields = ['id', 'member', 'group', 'amount', 'reason', 'status', 'requested_on', 'approved_on']
        read_only_fields = ['id', 'member', 'status', 'requested_on', 'approved_on']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Loan amount must be positive.")
        return value

    def validate_group(self, value):
        request = self.context.get('request')
        if not Membership.objects.filter(group=value, user=request.user).exists():
            raise serializers.ValidationError("You must be a member of this group to request a loan from it.")
        return value

    def validate(self, data):
        group = data.get('group')
        amount = data.get('amount')
        if group and amount:
            total_contributions = Contribution.objects.filter(group=group).aggregate(
                Sum('amount')
            )['amount__sum'] or Decimal('0')
            outstanding_loans = Loan.objects.filter(group=group, status='approved').aggregate(
                Sum('amount')
            )['amount__sum'] or Decimal('0')
            available = total_contributions - outstanding_loans

            if amount > (Decimal('0.7') * available):
                raise serializers.ValidationError(
                    "Requested amount exceeds the group's available loan limit."
                )
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['member'] = request.user
        return super().create(validated_data)
