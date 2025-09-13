import os
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
from django.shortcuts import render
from .models import User, CEO, HR, Manager, Employee, Attendance, Admin
from .serializers import UserSerializer, CEOSerializer, HRSerializer, ManagerSerializer, EmployeeSerializer, SuperUserCreateSerializer, UserRegistrationSerializer, AdminSerializer
from PIL import Image
import face_recognition
import numpy as np
import base64
from io import BytesIO

class SignupView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'user': serializer.data, 'message': 'Signup successful'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        role = request.data.get('role')
        if not email or not password or not role:
            return Response(
                {'error': 'Email, password, and role are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        user = authenticate(request, username=email, password=password)  # assumes USERNAME_FIELD='email'
        if user is not None:
            if user.role != role:
                return Response({'error': 'Role does not match'}, status=status.HTTP_403_FORBIDDEN)
            serializer = UserSerializer(user)
            return Response({'user': serializer.data, 'message': 'Login successful'}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class UserListView(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)  # many=True is critical
        return Response(serializer.data, status=status.HTTP_200_OK)

# CEO Views
class CEOListCreateView(generics.ListCreateAPIView):
    queryset = CEO.objects.all()
    serializer_class = CEOSerializer

# HR Views
class HRListCreateView(generics.ListCreateAPIView):
    queryset = HR.objects.all()
    serializer_class = HRSerializer

# Manager Views
class ManagerListCreateView(generics.ListCreateAPIView):
    queryset = Manager.objects.all()
    serializer_class = ManagerSerializer

# Employee Views
class EmployeeListCreateView(generics.ListCreateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

# Admin Views
class AdminListCreateView(generics.ListCreateAPIView):
    queryset = Admin.objects.all()
    serializer_class = AdminSerializer

class CreateSuperUserView(APIView):
    def post(self, request):
        serializer = SuperUserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  # Calls create_superuser method from UserManager
            return Response(
                {
                    'message': 'Superuser created successfully',
                    'email': user.email,
                    'role': user.role
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def approve_user(request):
    email = request.data.get('email')
    if not email:
        return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        user = User.objects.get(email=email)
        user.is_staff = True  # Mark user as staff (approved)
        user.save()
        return Response({'success': True, 'email': email})
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def reject_user(request):
    email = request.data.get('email')
    if not email:
        return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        user = User.objects.get(email=email)
        user.delete()  # Delete user (rejected)
        return Response({'success': True, 'email': email})
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


# =====================
# Load known faces
# =====================
KNOWN_FACES_DIR = 'C:/Users/Abhishek/Desktop/hrms_backend/hrms/images'
known_face_encodings = []
known_face_names = []

for filename in os.listdir(KNOWN_FACES_DIR):
    if filename.lower().endswith(('.jpg', '.png')):
        image_path = os.path.join(KNOWN_FACES_DIR, filename)
        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)
        if encodings:
            known_face_encodings.append(encodings[0])
            username, _ = os.path.splitext(filename)  # e.g., Abhi from Abhi.jpg
            known_face_names.append(username.lower())
            print(f"Loaded known face: {username.lower()}")

# =====================
# Helper function: get email by username with partial match
# =====================
def get_email_by_username(username):
    username = username.lower()
    for model in [HR, Employee, CEO, Manager, Admin]:
        all_fullnames = list(model.objects.values_list('fullname', flat=True))
        print(f"Checking in {model.__name__}: {all_fullnames}")
        objs = model.objects.filter(fullname__icontains=username)
        if objs.exists():
            email = objs.first().email.email
            print(f"[get_email_by_username] Found email {email} for username {username} in {model.__name__}")
            return email
    print(f"[get_email_by_username] No email found for username {username}")
    return None

# =====================
# Check if email exists
# =====================
def is_email_exists(email):
    exists = any([
        HR.objects.filter(email=email).exists(),
        Employee.objects.filter(email=email).exists(),
        CEO.objects.filter(email=email).exists(),
        Manager.objects.filter(email=email).exists(),
        Admin.objects.filter(email=email).exists()
    ])
    print(f"[is_email_exists] Email {email} exists: {exists}")
    return exists

# =====================
# Mark attendance by email with User instance assignment
# =====================
def mark_attendance_by_email(email_str):
    if not is_email_exists(email_str):
        print(f"[mark_attendance_by_email] Email {email_str} not found in user models. Attendance not marked.")
        return None

    today = timezone.localdate()
    now_time = timezone.localtime().time()
    print(f"[mark_attendance_by_email] Processing attendance for {email_str} on {today} at {now_time}")

    try:
        user_instance = User.objects.get(email=email_str)
    except User.DoesNotExist:
        print(f"[mark_attendance_by_email] User instance not found for email {email_str}")
        return None

    try:
        attendance = Attendance.objects.get(email=user_instance, date=today)
        if attendance.check_out is None:
            attendance.check_out = now_time
            attendance.save()
            print(f"[mark_attendance_by_email] Updated check_out for {email_str} at {now_time}")
    except Attendance.DoesNotExist:
        try:
            attendance = Attendance.objects.create(
                email=user_instance,  # Assign User instance
                date=today,
                check_in=now_time
            )
            print(f"[mark_attendance_by_email] Created new attendance record for {email_str} at {now_time}")
        except Exception as e:
            print(f"[mark_attendance_by_email ERROR] Failed to save attendance for {email_str}: {e}")
            return None

    return attendance

# =====================
# Face recognition page render
# =====================
def face_recognition_page(request):
    return render(request, "face_recognition.html")

# =====================
# Face recognition API view
# =====================
def recognize_face(request):
    if request.method == "POST":
        data = json.loads(request.body)
        image_data = data.get("image", "")
        if not image_data:
            return JsonResponse({"error": "No image data provided"}, status=400)

        image_data = image_data.split(",")[1]  # strip data header
        image_bytes = base64.b64decode(image_data)
        img = Image.open(BytesIO(image_bytes)).convert('RGB')
        img_np = np.array(img)

        face_encodings = face_recognition.face_encodings(img_np)

        username = "No face detected"
        email = None
        confidence = 0
        attendance = None

        if face_encodings:
            face_encoding = face_encodings[0]
            distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(distances)
            best_distance = distances[best_match_index]

            if best_distance < 0.6:
                username = known_face_names[best_match_index]
                email = get_email_by_username(username)
                confidence = round((1 - best_distance) * 100, 2)
            else:
                username = "Unknown"
                email = None

        print(f"[recognize_face] Username: {username}, Email: {email}, Confidence: {confidence}%")

        if email:
            attendance = mark_attendance_by_email(email)
        else:
            print("[recognize_face] No valid email found; attendance not marked.")

        return JsonResponse({
            "username": username,
            "email": email,
            "confidence": f"{confidence}%" if email else "",
            "check_in": str(attendance.check_in) if attendance else "",
            "check_out": str(attendance.check_out) if attendance else ""
        })
    else:
        return JsonResponse({"error": "Invalid method"}, status=405)

# =====================
# Today attendance view
# =====================
def today_attendance(request):
    today = timezone.localdate()
    attendances = Attendance.objects.filter(date=today)

    data = [
        {
            "email": att.email.email,
            "date": att.date,
            "check_in": str(att.check_in) if att.check_in else "",
            "check_out": str(att.check_out) if att.check_out else ""
        }
        for att in attendances
    ]

    return JsonResponse({"attendances": data})

# Helper function to handle PUT
def handle_put(request, ModelClass, SerializerClass):
    try:
        data = json.loads(request.body)
        email = data.get("email")
        if not email:
            return JsonResponse({"error": "Email field is required"}, status=400)
        instance = ModelClass.objects.get(email=email)
    except ModelClass.DoesNotExist:
        return JsonResponse({"error": f"{ModelClass.__name__} not found"}, status=404)
    serializer = SerializerClass(instance, data=data, partial=True)  # partial=True allows partial updates
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data)
    return JsonResponse(serializer.errors, status=400)


# Helper function to handle DELETE
def handle_delete(request, ModelClass):
    try:
        data = json.loads(request.body)
        email = data.get("email")
        if not email:
            return JsonResponse({"error": "Email field is required"}, status=400)
        
        # Get the instance in role table
        instance = ModelClass.objects.get(email=email)
        instance.delete()
        print(f"Deleted {ModelClass.__name__} record with email {email}")
        
        # Also delete corresponding User record
        from accounts.models import User  # import User model
        try:
            user = User.objects.get(email=email)
            user.delete()
            print(f"Deleted User record with email {email}")
        except User.DoesNotExist:
            print(f"No User record found to delete for email {email}")
        
        return JsonResponse({"message": f"{ModelClass.__name__} and User deleted successfully"})
    except ModelClass.DoesNotExist:
        return JsonResponse({"error": f"{ModelClass.__name__} not found"}, status=404)


@csrf_exempt
def ceo_list(request):
    if request.method == "GET":
        ceos = CEO.objects.all()
        data = CEOSerializer(ceos, many=True).data
        return JsonResponse(data, safe=False)
    elif request.method == "PUT":
        return handle_put(request, CEO, CEOSerializer)
    elif request.method == "DELETE":
        return handle_delete(request, CEO)

@csrf_exempt
def hr_list(request):
    if request.method == "GET":
        hrs = HR.objects.all()
        data = HRSerializer(hrs, many=True).data
        return JsonResponse(data, safe=False)
    elif request.method == "PUT":
        return handle_put(request, HR, HRSerializer)
    elif request.method == "DELETE":
        return handle_delete(request, HR)

@csrf_exempt
def manager_list(request):
    if request.method == "GET":
        managers = Manager.objects.all()
        data = ManagerSerializer(managers, many=True).data
        return JsonResponse(data, safe=False)
    elif request.method == "PUT":
        return handle_put(request, Manager, ManagerSerializer)
    elif request.method == "DELETE":
        return handle_delete(request, Manager)

@csrf_exempt
def employee_list(request):
    if request.method == "GET":
        employees = Employee.objects.all()
        data = EmployeeSerializer(employees, many=True).data
        return JsonResponse(data, safe=False)
    elif request.method == "PUT":
        return handle_put(request, Employee, EmployeeSerializer)
    elif request.method == "DELETE":
        return handle_delete(request, Employee)

@csrf_exempt
def admin_list(request):
    if request.method == "GET":
        admins = Admin.objects.all()
        data = AdminSerializer(admins, many=True).data
        return JsonResponse(data, safe=False)
    elif request.method == "PUT":
        return handle_put(request, Admin, AdminSerializer)
    elif request.method == "DELETE":
        return handle_delete(request, Admin)

