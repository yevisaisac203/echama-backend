# contributions/serializers.py
from rest_framework import serializers
from .models import Contribution
from users.serializers import UserSerializer
from groups.models import Group

class ContributionSerializer(serializers.ModelSerializer):
    member = UserSerializer(read_only=True)  # returned in responses
    # group is provided by client as group id (primary key)
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())

    class Meta:
        model = Contribution
        fields = ['id', 'member', 'group', 'amount', 'date']
        read_only_fields = ['id', 'member']

    def validate_amount(self, value):
        # field-level validation: make sure amount > 0
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0.")
        return value

    def create(self, validated_data):
        # set the member to the current user (from context) before creating
        request = self.context.get('request')
        validated_data['member'] = request.user
        return super().create(validated_data)
