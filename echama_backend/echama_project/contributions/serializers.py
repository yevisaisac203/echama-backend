# contributions/serializers.py
from rest_framework import serializers
from .models import Contribution
from users.serializers import UserSerializer
from groups.models import Group

class ContributionSerializer(serializers.ModelSerializer):
    member = UserSerializer(read_only=True) 
    
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())

    class Meta:
        model = Contribution
        fields = ['id', 'member', 'group', 'amount', 'date']
        read_only_fields = ['id', 'member']

    def validate_amount(self, value):
        
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0.")
        return value

    def create(self, validated_data):
       
        request = self.context.get('request')
        validated_data['member'] = request.user
        return super().create(validated_data)
