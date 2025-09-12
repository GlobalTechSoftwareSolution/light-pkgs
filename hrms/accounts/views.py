from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import User, CEO, HR, Manager, Employee
from .serializers import UserSerializer, CEOSerializer, HRSerializer, ManagerSerializer, EmployeeSerializer, SuperUserCreateSerializer, UserRegistrationSerializer

class SignupView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'user': serializer.data, 'message': 'Signup successful'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        role = request.data.get('role')  # get role from request data
        
        # Validate required fields including role
        if not username or not password or not role:
            return Response(
                {'error': 'Username, password, and role are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(username=username, password=password)
        if user:
            # Check if user's role matches the role in login request
            if hasattr(user, 'role') and user.role == role:
                serializer = UserSerializer(user)
                return Response({'user': serializer.data, 'message': 'Login successful'}, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': 'Role does not match'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
        
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

class CEODetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CEO.objects.all()
    serializer_class = CEOSerializer

# HR Views
class HRListCreateView(generics.ListCreateAPIView):
    queryset = HR.objects.all()
    serializer_class = HRSerializer

class HRDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = HR.objects.all()
    serializer_class = HRSerializer

# Manager Views
class ManagerListCreateView(generics.ListCreateAPIView):
    queryset = Manager.objects.all()
    serializer_class = ManagerSerializer

class ManagerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Manager.objects.all()
    serializer_class = ManagerSerializer

# Employee Views
class EmployeeListCreateView(generics.ListCreateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

class EmployeeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

class CreateSuperUserView(APIView):
    def post(self, request):
        serializer = SuperUserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  # serializer handles superuser creation
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
        user.is_staff = True
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
        user.delete()
        return Response({'success': True, 'email': email})
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Employee, HR, CEO, Admin
from .serializers import EmployeeSerializer, HRSerializer, CEOSerializer, AdminSerializer

@api_view(['GET'])
def employee_list(request):
    employees = Employee.objects.all()
    serializer = EmployeeSerializer(employees, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def hr_list(request):
    hr_users = HR.objects.all()
    serializer = HRSerializer(hr_users, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def manager_list(request):
    employees = Manager.objects.all()
    serializer = ManagerSerializer(employees, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def ceo_list(request):
    hr_users = CEO.objects.all()
    serializer = CEOSerializer(hr_users, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def admin_list(request):
    hr_users = Admin.objects.all()
    serializer = CEOSerializer(hr_users, many=True)
    return Response(serializer.data)

# from django.http import JsonResponse
# from PIL import Image
# import numpy as np
# import base64
# from io import BytesIO
# import face_recognition
# import os

# KNOWN_FACES_DIR = 'C:/Users/Abhishek/Desktop/hrms-test/hrms-test/images'
# known_face_encodings = []
# known_face_names = []

# # Load known faces once
# def load_known_faces():
#     for filename in os.listdir(KNOWN_FACES_DIR):
#         if filename.lower().endswith(('.jpg', '.png')):
#             image_path = os.path.join(KNOWN_FACES_DIR, filename)
#             image = face_recognition.load_image_file(image_path)
#             encodings = face_recognition.face_encodings(image)
#             if encodings:
#                 known_face_encodings.append(encodings[0])
#                 name, _ = os.path.splitext(filename)
#                 known_face_names.append(name)

# load_known_faces()


# def recognize_face(request):
#     import json
#     if request.method == "POST":
#         data = json.loads(request.body)
#         image_data = data["image"].split(",")[1]

#         # --- START OF REPLACEMENT ---
#         image_bytes = base64.b64decode(image_data)
#         img = Image.open(BytesIO(image_bytes)).convert('RGB')
#         img_np = np.array(img)

#         face_encodings = face_recognition.face_encodings(img_np)
#         # --- END OF REPLACEMENT ---

#         if face_encodings:
#             face_encoding = face_encodings[0]
#             distances = face_recognition.face_distance(known_face_encodings, face_encoding)
#             best_match_index = np.argmin(distances)
#             best_distance = distances[best_match_index]

#             if best_distance < 0.6:
#                 name = known_face_names[best_match_index]
#                 confidence = (1 - best_distance) * 100
#             else:
#                 name = "Unknown"
#                 confidence = 0
#         else:
#             name = "No face detected"
#             confidence = 0

#         return JsonResponse({"name": name, "confidence": confidence})

# from django.shortcuts import render

# def face_recognition_page(request):
#     return render(request, "face_recognition.html")

from django.http import JsonResponse
from django.utils import timezone
from PIL import Image
import face_recognition
import numpy as np
import base64
from io import BytesIO
import os
from .models import Attendance
from accounts.models import User  # your custom User model

# Path to known profile images
KNOWN_FACES_DIR = 'C:/Users/Abhishek/Desktop/hrms-test/hrms-test/images'
known_face_encodings = []
known_face_names = []

# Load known faces once
for filename in os.listdir(KNOWN_FACES_DIR):
    if filename.lower().endswith(('.jpg', '.png')):
        image_path = os.path.join(KNOWN_FACES_DIR, filename)
        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)
        if encodings:
            known_face_encodings.append(encodings[0])
            username, _ = os.path.splitext(filename)  # e.g., Abhi from Abhi.jpg
            known_face_names.append(username)

def recognize_face(request):
    import json
    if request.method == "POST":
        data = json.loads(request.body)
        image_data = data["image"].split(",")[1]
        image_bytes = base64.b64decode(image_data)
        img = Image.open(BytesIO(image_bytes)).convert('RGB')
        img_np = np.array(img)

        # Detect face encodings
        face_encodings = face_recognition.face_encodings(img_np)

        if face_encodings:
            face_encoding = face_encodings[0]
            distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(distances)
            best_distance = distances[best_match_index]

            if best_distance < 0.6:
                username = known_face_names[best_match_index]

                # Fetch role from User table
                try:
                    user = User.objects.get(email__iexact=username+"@domain.com")  
                    # adjust email format if your filenames do not match email exactly
                    role = user.role
                except User.DoesNotExist:
                    role = "Unknown"
            else:
                username = "Unknown"
                role = "Unknown"
        else:
            username = "No face detected"
            role = "Unknown"

        # Mark attendance
        today = timezone.localdate()
        now_time = timezone.localtime().time()
        attendance = None
        if username not in ["Unknown", "No face detected"]:
            attendance, created = Attendance.objects.get_or_create(
                username=username,
                date=today,
                defaults={"role": role, "check_in": now_time}
            )
            if not created and attendance.check_out is None:
                attendance.check_out = now_time
                attendance.save()

        return JsonResponse({
            "username": username,
            "role": role,
            "check_in": str(attendance.check_in) if attendance else "",
            "check_out": str(attendance.check_out) if attendance else ""
        })
