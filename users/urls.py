# users/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib.auth import views as auth_views # إضافة هذا السطر
from .views import (
    # User Views
    RegisterView, LoginView, DoctorProfileView,
    AdminListUsers, AdminDeleteUser, AdminUpdateRole,
    # Medical Views
    SpecializationViewSet, 
    DiseaseViewSet, 
    AppointmentViewSet,
    PrescriptionViewSet,
    DoctorListView,
    DoctorsByDiseaseView,
    PatientListView,
    # New / Updated
    SendPasswordResetEmailView, # تم تغيير الاسم ليعبر عن الوظيفة الجديدة
    AdminDoctorDetailView,
)

# إنشاء الـ Router للـ ViewSets
router = DefaultRouter()
router.register(r'specializations', SpecializationViewSet, basename='specialization')
router.register(r'diseases', DiseaseViewSet, basename='disease')
router.register(r'appointments', AppointmentViewSet, basename='appointment')
router.register(r'prescriptions', PrescriptionViewSet, basename='prescription')

urlpatterns = [
    # 1. الموجه التلقائي (Specializations, Diseases, Appointments, Prescriptions)
    path('', include(router.urls)),

    # 2. مسارات الحسابات (Auth)
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    
    # 3. مسارات الأطباء (Doctors)
    path('doctors/', DoctorListView.as_view(), name='doctor-list'),
    path('doctors/me/', DoctorProfileView.as_view(), name='doctor-profile-me'),
    path('doctors/by_disease/<int:disease_id>/', DoctorsByDiseaseView.as_view(), name='doctors-by-disease'),

    # 4. مسارات الإدارة (Admin)
    path("admin/list/", AdminListUsers.as_view()),
    path("admin/delete/<int:user_id>/", AdminDeleteUser.as_view()),
    path("admin/update-role/<int:user_id>/", AdminUpdateRole.as_view()),
    path('admin/patients/', PatientListView.as_view(), name='admin-patients-list'),

    # 5. Reset Password Flow
    # API لاستقبال الإيميل من فلاتر وإرسال الرابط
    path('api/send-reset-email/', SendPasswordResetEmailView.as_view(), name='send-reset-email'),
    # صفحات الويب التي يفتحها المستخدم من الإيميل
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # 6. Admin Doctor Management
    path('admin/doctors/<int:doctor_id>/', AdminDoctorDetailView.as_view(), name='admin-doctor-detail'),
]