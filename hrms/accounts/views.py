import os
import json
import base64
import numpy as np
import face_recognition
from PIL import Image
from io import BytesIO
from rest_framework import status
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.conf import settings
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404
from .models import User, CEO, HR, Manager, Employee, Attendance, Admin, Leave, Payroll
from .serializers import UserSerializer, CEOSerializer, HRSerializer, ManagerSerializer, EmployeeSerializer, SuperUserCreateSerializer, UserRegistrationSerializer, AdminSerializer

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
KNOWN_FACES_DIR = os.path.join(settings.BASE_DIR, "images")
known_face_encodings = []
known_face_names = []

if os.path.exists(KNOWN_FACES_DIR):
    for filename in os.listdir(KNOWN_FACES_DIR):
        if filename.lower().endswith(('.jpg', '.png')):
            image_path = os.path.join(KNOWN_FACES_DIR, filename)
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                known_face_encodings.append(encodings[0])
                username, _ = os.path.splitext(filename)
                known_face_names.append(username.lower())
                print(f"Loaded known face: {username.lower()}")
else:
    print(f"[WARNING] Known faces directory {KNOWN_FACES_DIR} not found. Skipping face loading.")

# =====================
# Helper: get email by username (partial match)
# =====================
def get_email_by_username(username):
    username = username.lower()
    for model in [HR, Employee, CEO, Manager, Admin]:
        for obj in model.objects.all():
            full_name_lower = obj.fullname.lower()
            if any(part.startswith(username) for part in full_name_lower.split()):
                email = obj.email.email
                print(f"[get_email_by_username] Found email {email} for username {username} in {model._name_}")
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
# Mark attendance by email
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
        attendance = Attendance.objects.get(email=user_instance)
        if attendance.check_out is None:
            attendance.check_out = now_time
            attendance.save()
            print(f"[mark_attendance_by_email] Updated check_out for {email_str} at {now_time}")
    except Attendance.DoesNotExist:
        try:
            attendance = Attendance.objects.create(
                email=user_instance,  # email is PK
                date=today,
                check_in=now_time
            )
            print(f"[mark_attendance_by_email] Created new attendance record for {email_str} at {now_time}")
        except Exception as e:
            print(f"[mark_attendance_by_email ERROR] Failed to save attendance for {email_str}: {e}")
            return None

    return attendance

# =====================
# Render face recognition page
# =====================
def face_recognition_page(request):
    return render(request, "face_recognition.html")

# =====================
# Face recognition API
# =====================
@csrf_exempt
def recognize_face(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    try:
        data = json.loads(request.body)
        image_data = data.get("image", "")
        if not image_data:
            return JsonResponse({"error": "No image data provided"}, status=400)

        image_data = image_data.split(",")[1]  # Remove base64 header
        image_bytes = base64.b64decode(image_data)
        img = Image.open(BytesIO(image_bytes)).convert('RGB')
        img_np = np.array(img)
    except Exception as e:
        return JsonResponse({"error": f"Failed to process image: {e}"}, status=400)

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
        return JsonResponse({"error": f"{ModelClass._name_} not found"}, status=404)
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
        print(f"Deleted {ModelClass._name_} record with email {email}")
        
        # Also delete corresponding User record
        from accounts.models import User  # import User model
        try:
            user = User.objects.get(email=email)
            user.delete()
            print(f"Deleted User record with email {email}")
        except User.DoesNotExist:
            print(f"No User record found to delete for email {email}")
        
        return JsonResponse({"message": f"{ModelClass._name_} and User deleted successfully"})
    except ModelClass.DoesNotExist:
        return JsonResponse({"error": f"{ModelClass._name_} not found"}, status=404)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    lookup_field = 'email'

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return UserRegistrationSerializer
        return UserSerializer

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    lookup_field = 'email'

class HRViewSet(viewsets.ModelViewSet):
    queryset = HR.objects.all()
    serializer_class = HRSerializer
    lookup_field = 'email'

class ManagerViewSet(viewsets.ModelViewSet):
    queryset = Manager.objects.all()
    serializer_class = ManagerSerializer
    lookup_field = 'email'

class AdminViewSet(viewsets.ModelViewSet):
    queryset = Admin.objects.all()
    serializer_class = AdminSerializer
    lookup_field = 'email'

class CEOViewSet(viewsets.ModelViewSet):
    queryset = CEO.objects.all()
    serializer_class = CEOSerializer
    lookup_field = 'email'

@csrf_exempt
def apply_leave(request):
    """Employee applies for leave. If leave already exists, return error."""
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method allowed"}, status=405)

    try:
        data = json.loads(request.body)
        email = data.get("email")
        user = get_object_or_404(User, email=email)

        # Check if leave already exists for this user
        if Leave.objects.filter(email=user).exists():
            return JsonResponse({"error": "You already have a leave request. Wait for it to be processed."}, status=400)

        leave = Leave.objects.create(
            email=user,
            department=data.get("department"),
            start_date=data.get("start_date"),
            end_date=data.get("end_date"),
            leave_type=data.get("leave_type", ""),
            reason=data.get("reason", ""),
            status="Pending"
        )

        return JsonResponse({
            "message": "Leave request submitted successfully",
            "leave": {
                "email": leave.email.email,
                "department": leave.department,
                "start_date": str(leave.start_date),
                "end_date": str(leave.end_date),
                "leave_type": leave.leave_type,
                "reason": leave.reason,
                "status": leave.status
            }
        }, status=201)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def update_leave_status(request, email):
    """Manager approves or rejects leave."""
    if request.method != "PATCH":
        return JsonResponse({"error": "Only PATCH method allowed"}, status=405)

    try:
        user = get_object_or_404(User, email=email)
        leave = get_object_or_404(Leave, email=user)

        data = json.loads(request.body)
        new_status = data.get("status")

        if new_status not in ["Approved", "Rejected"]:
            return JsonResponse({"error": "Invalid status. Must be Approved or Rejected."}, status=400)

        leave.status = new_status
        leave.save()

        return JsonResponse({
            "message": f"Leave request {new_status}",
            "leave": {
                "email": leave.email.email,
                "department": leave.department,
                "start_date": str(leave.start_date),
                "end_date": str(leave.end_date),
                "leave_type": leave.leave_type,
                "reason": leave.reason,
                "status": leave.status
            }
        }, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
    
from django.utils import timezone
from django.http import JsonResponse
from .models import Leave

def leaves_today(request):
    """List all employees on leave today"""
    if request.method != "GET":
        return JsonResponse({"error": "Only GET method allowed"}, status=405)

    today = timezone.localdate()
    leaves = Leave.objects.filter(
        status="Approved",
        start_date__lte=today,
        end_date__gte=today
    )

    result = []
    for leave in leaves:
        result.append({
            "email": leave.email.email,
            "department": leave.department,
            "start_date": str(leave.start_date),
            "end_date": str(leave.end_date),
            "leave_type": leave.leave_type,
            "reason": leave.reason,
            "status": leave.status
        })

    return JsonResponse({"leaves_today": result}, status=200)