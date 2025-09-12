from django.urls import path
from .views import (
    LoginView, UserListView,
    CEOListCreateView, CEODetailView,
    HRListCreateView, HRDetailView,
    ManagerListCreateView, ManagerDetailView,
    EmployeeListCreateView, EmployeeDetailView,
    CreateSuperUserView, SignupView, approve_user, reject_user, face_recognition_page, recognize_face
)
from . import views

urlpatterns = [
    path('signup/', SignupView.as_view(), name='user-signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('users/', UserListView.as_view(), name='user-list'),

    # CEO
    path('ceos/', CEOListCreateView.as_view(), name='ceo-list-create'),
    path('ceos/<int:pk>/', CEODetailView.as_view(), name='ceo-detail'),

    # HR
    path('hrs/', HRListCreateView.as_view(), name='hr-list-create'),
    path('hrs/<int:pk>/', HRDetailView.as_view(), name='hr-detail'),

    # Manager
    path('managers/', ManagerListCreateView.as_view(), name='manager-list-create'),
    path('managers/<int:pk>/', ManagerDetailView.as_view(), name='manager-detail'),

    # Employee
    path('employees/', EmployeeListCreateView.as_view(), name='employee-list-create'),
    path('employees/<int:pk>/', EmployeeDetailView.as_view(), name='employee-detail'),

    path('create-superuser/', CreateSuperUserView.as_view(), name='create-superuser'),

    path('approve/', approve_user),
    path('reject/', reject_user),

    path('employee/', views.employee_list),
    path('hr/', views.hr_list),
    path('ceo/', views.ceo_list),
    path('manager/', views.admin_list),
    path('admin/', views.admin_list),

    path("face_recognition/", face_recognition_page, name="face_recognition_page"),
    path("recognize_face/", recognize_face, name="recognize_face"),
]
