from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True ,required=True ,min_length=8)
    
    class Meta:
        model= User
        fields= ['id', 'username', 'email', 'password', 'first_name', 'last_name', 'role']
        read_only_fields = ['id','role']
        
    def create(self, validated_data):
     password = validated_data.pop('password')     
     user = User(**validated_data)                 
     user.set_password(password)                   
     user.save()                                   
     return user