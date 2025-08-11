# loans/serializers.py
from rest_framework import serializers
from .models import Loan
from users.serializers import UserSerializer
from groups.models import Group
from django.db.models import Sum
from contributions.models import Contribution

class LoanSerializer(serializers.ModelSerializer):
    member = UserSerializer(read_only=True)
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())

    class Meta:
        model = Loan
        fields = ['id', 'member', 'group', 'amount', 'reason', 'status', 'requested_on', 'approved_on']
        read_only_fields = ['id', 'member', 'status', 'requested_on', 'approved_on']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Loan amount must be positive.")
        return value

    def validate(self, data):
        
        group = data.get('group')
        amount = data.get('amount')
        
        total = Contribution.objects.filter(group=group).aggregate(Sum('amount'))['amount__sum'] or 0

        if amount and total and amount > (0.7 * total):
            raise serializers.ValidationError("Requested amount exceeds allowed limit for this group.")
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['member'] = request.user
        
        return super().create(validated_data)
