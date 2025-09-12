from rest_framework import serializers
from .models import User, CEO, HR, Manager, Employee, Admin

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['email', 'password', 'role']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'role', 'is_staff']

class CEOSerializer(serializers.ModelSerializer):
    class Meta:
        model = CEO
        fields = '__all__'

class HRSerializer(serializers.ModelSerializer):
    class Meta:
        model = HR
        fields = '__all__'

class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manager
        fields = '__all__'

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'

class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = '__all__'

class SuperUserCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_email(self, value):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def create(self, validated_data):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_superuser(
            email=validated_data['email'],
            password=validated_data['password'],
            role='CEO'  # Default superuser role, adapt if needed
        )
        return user
