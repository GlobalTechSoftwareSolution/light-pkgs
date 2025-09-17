from rest_framework import serializers
from .models import User, CEO, HR, Manager, Employee, Admin, Leave, Attendance
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['email', 'password', 'role']

    def create(self, validated_data):
        # Always hash password when creating
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        # Ensure password is hashed when updating too
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'role', 'is_staff']


class CEOSerializer(serializers.ModelSerializer):
    class Meta:
        model = CEO
        fields = '_all_'

class HRSerializer(serializers.ModelSerializer):
    class Meta:
        model = HR
        fields = '_all_'

class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manager
        fields = '_all_'

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '_all_'

class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = '_all_'

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
            role='admin'  # Default superuser role, adapt if needed
        )
        return user


class LeaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leave
        fields = '_all_'
        read_only_fields = ['status', 'applied_on']   # status set to Pending automatically


from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        token["email"] = user.email
        token["role"] = getattr(user, "role", None)
        
        return token

from rest_framework import serializers
from .models import User

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "role"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
class AttendanceSerializer(serializers.ModelSerializer):
    email = serializers.StringRelatedField()  # shows the user's email

    class Meta:
        model = Attendance
        fields = ['email', 'date', 'check_in', 'check_out']