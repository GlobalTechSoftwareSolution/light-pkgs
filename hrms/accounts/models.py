from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone


# =====================
# Custom User Manager
# =====================
class UserManager(BaseUserManager):
    def create_user(self, email, role, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, role='CEO', password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, role, password, **extra_fields)


# =====================
# User Model
# =====================
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(primary_key=True, max_length=254)
    role = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['role']

    objects = UserManager()

    def __str__(self):
        return f"{self.email} ({self.role})"


# =====================
# HR Model
# =====================
class HR(models.Model):
    email = models.OneToOneField(User, on_delete=models.CASCADE, to_field='email', primary_key=True)
    fullname = models.CharField(max_length=255)
    age = models.IntegerField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    department = models.CharField(max_length=100, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    date_joined = models.DateField(null=True, blank=True)
    qualification = models.CharField(max_length=255, null=True, blank=True)
    skills = models.TextField(null=True, blank=True)
    profile_picture = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.fullname} (HR)"


# =====================
# CEO Model
# =====================
class CEO(models.Model):
    email = models.OneToOneField(User, on_delete=models.CASCADE, to_field='email', primary_key=True)
    fullname = models.CharField(max_length=255)
    age = models.IntegerField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    office_address = models.TextField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    date_joined = models.DateField(null=True, blank=True)
    total_experience = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    profile_picture = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.fullname} (CEO)"


# =====================
# Manager Model
# =====================
class Manager(models.Model):
    email = models.OneToOneField(User, on_delete=models.CASCADE, to_field='email', primary_key=True)
    fullname = models.CharField(max_length=255)
    age = models.IntegerField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    department = models.CharField(max_length=100, null=True, blank=True)
    team_size = models.IntegerField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    date_joined = models.DateField(null=True, blank=True)
    manager_level = models.CharField(max_length=50, null=True, blank=True)
    projects_handled = models.TextField(null=True, blank=True)
    profile_picture = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.fullname} (Manager)"


# =====================
# Employee Model
# =====================
class Employee(models.Model):
    email = models.OneToOneField(User, on_delete=models.CASCADE, to_field='email', primary_key=True)
    fullname = models.CharField(max_length=255)
    age = models.IntegerField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    department = models.CharField(max_length=100, null=True, blank=True)
    designation = models.CharField(max_length=100, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    date_joined = models.DateField(null=True, blank=True)
    reports_to = models.ForeignKey(Manager, on_delete=models.SET_NULL, to_field='email', null=True, blank=True)
    skills = models.TextField(null=True, blank=True)
    profile_picture = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.fullname} (Employee)"


# =====================
# Admin Model
# =====================
class Admin(models.Model):
    email = models.OneToOneField(User, on_delete=models.CASCADE, to_field='email', primary_key=True)
    fullname = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, null=True, blank=True)
    office_address = models.TextField(null=True, blank=True)
    profile_picture = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.fullname} (Admin)"


# =====================
# Attendance Model
# =====================
from django.db import models
from django.utils import timezone


class Attendance(models.Model):
    email = models.OneToOneField(User, on_delete=models.CASCADE, to_field='email', primary_key=True)
    date = models.DateField(default=timezone.localdate)
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['email', 'date'], name='unique_attendance_per_day')
        ]
        ordering = ['-date']

    def __str__(self):
        return f"{self.email.email} ({self.email.role}) - {self.date}"

from django.db import models
from django.utils import timezone
from accounts.models import User  # Adjust import if needed

class Leave(models.Model):
    email = models.OneToOneField(User, on_delete=models.CASCADE, to_field='email', primary_key=True)
    department = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    leave_type = models.CharField(max_length=50, null=True, blank=True)  # e.g. Sick, Casual, Paid
    reason = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, default='Pending')  # e.g. Pending, Approved, Rejected
    applied_on = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-applied_on']

    def __str__(self):
        return f"{self.email.email} - {self.department} Leave from {self.start_date} to {self.end_date} [{self.status}]"
