from django.urls import path
from .views import (
    LoginView, UserListView,
    CEOListCreateView,
    HRListCreateView, 
    ManagerListCreateView,
    EmployeeListCreateView, AdminListCreateView,
    CreateSuperUserView, SignupView, approve_user, reject_user, face_recognition_page, recognize_face, today_attendance
)
from .views import ceo_list, hr_list, manager_list, employee_list, admin_list

urlpatterns = [
    path('signup/', SignupView.as_view(), name='user-signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('users/', UserListView.as_view(), name='user-list'),

    path('ceos/', CEOListCreateView.as_view(), name='ceo-list-create'),
    path('hrs/', HRListCreateView.as_view(), name='hr-list-create'),
    path('managers/', ManagerListCreateView.as_view(), name='manager-list-create'),
    path('employees/', EmployeeListCreateView.as_view(), name='employee-list-create'),

    path('admins/', AdminListCreateView.as_view(), name='employee-list-create'),
    path('create-superuser/', CreateSuperUserView.as_view(), name='create-superuser'),

    path('approve/', approve_user),
    path('reject/', reject_user),

    path("face_recognition/", face_recognition_page, name="face_recognition_page"),
    path("recognize_face/", recognize_face, name="recognize_face"),

    # path("mark_attendance/", mark_attendance_by_email, name="mark_attendance"),
    path("today_attendance/", today_attendance, name="today_attendance"),

    path('ceo/', ceo_list, name='ceo_list'),          # GET/PUT/DELETE CEO records
    path('hr/', hr_list, name='hr_list'),             # GET/PUT/DELETE HR records
    path('manager/', manager_list, name='manager_list'),   # GET/PUT/DELETE Manager records
    path('employee/', employee_list, name='employee_list'), # GET/PUT/DELETE Employee records
    path('admin/', admin_list, name='admin_list'),    # GET/PUT/DELETE Admin records
]
