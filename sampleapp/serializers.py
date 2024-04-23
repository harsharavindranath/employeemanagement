from rest_framework import serializers
from .models import *


class RegisterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'user_type']

class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username']

class AdminUserhirarchyupdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username','user_type','first_name','last_name']

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task  
        fields = '__all__'