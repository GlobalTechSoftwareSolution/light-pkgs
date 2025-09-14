from django.urls import path
from accounts.views import (LoginView, CreateSuperUserView, SignupView, approve_user, reject_user,

#  face_recognition_page,
# recognize_face, 
today_attendance, UserViewSet, EmployeeViewSet, HRViewSet, ManagerViewSet, AdminViewSet, CEOViewSet )

urlpatterns = [
    path('signup/', SignupView.as_view(), name='user-signup'),
    path('login/', LoginView.as_view(), name='login'),
    # path('users/', UserListView.as_view(), name='user-list'),

    # path('ceos/', CEOListCreateView.as_view(), name='ceo-list-create'),
    # path('hrs/', HRListCreateView.as_view(), name='hr-list-create'),
    # path('managers/', ManagerListCreateView.as_view(), name='manager-list-create'),
    # path('employees/', EmployeeListCreateView.as_view(), name='employee-list-create'),
    # path('admins/', AdminListCreateView.as_view(), name='employee-list-create'),
    # path('create-superuser/', CreateSuperUserView.as_view(), name='create-superuser'),

    path('approve/', approve_user),
    path('reject/', reject_user),

    # path("attendance/", face_recognition_page, name="face_recognition_page"),
    # path("recognize_face/", recognize_face, name="recognize_face"),

    path("today_attendance/", today_attendance, name="today_attendance"),

    # Employee
    path('users/', UserViewSet.as_view({'get': 'list', 'post': 'create'}), name='employee-list'),
    path('users/<str:email>/', UserViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='users-detail'),

    # Employee
    path('employees/', EmployeeViewSet.as_view({'get': 'list', 'post': 'create'}), name='employee-list'),
    path('employees/<str:email>/', EmployeeViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='employee-detail'),

    # HR
    path('hrs/', HRViewSet.as_view({'get': 'list', 'post': 'create'}), name='hr-list'),
    path('hrs/<str:email>/', HRViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='hr-detail'),

    # Manager
    path('managers/', ManagerViewSet.as_view({'get': 'list', 'post': 'create'}), name='manager-list'),
    path('managers/<str:email>/', ManagerViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='manager-detail'),

    # Admin
    path('admins/', AdminViewSet.as_view({'get': 'list', 'post': 'create'}), name='admin-list'),
    path('admins/<str:email>/', AdminViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='admin-detail'),

    # CEO
    path('ceos/', CEOViewSet.as_view({'get': 'list', 'post': 'create'}), name='ceo-list'),
    path('ceos/<str:email>/', CEOViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='ceo-detail'),
]
