# medical_data/views.py

from rest_framework import viewsets, generics, permissions, filters, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .models import Specialization, Disease, Appointment
from .serializers import (
    SpecializationSerializer, 
    DiseaseSerializer, 
    AppointmentSerializer,
    DoctorProfileSerializer
)
from users.models import DoctorProfile, UserProfile # تم إضافة UserProfile للاستخدام في get_queryset

# 1. ViewSet لعرض التخصصات
class SpecializationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    قائمة تخصصات الأطباء (قراءة فقط)
    /api/specializations/
    """
    queryset = Specialization.objects.all()
    serializer_class = SpecializationSerializer
    permission_classes = [AllowAny] 


# 2. ViewSet لعرض الأمراض
class DiseaseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    قائمة الأمراض وتفاصيلها (قراءة فقط)
    /api/diseases/
    """
    queryset = Disease.objects.all()
    serializer_class = DiseaseSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name_ar', 'specialization__name_ar']


# 3. View لعرض قائمة الأطباء
class DoctorListView(generics.ListAPIView):
    """
    قائمة الأطباء مع إمكانية البحث حسب التخصص
    /api/doctors/
    """
    queryset = DoctorProfile.objects.all()
    serializer_class = DoctorProfileSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['user_profile__user__username', 'specialization__name_ar']


# 4. ViewSet لإدارة المواعيد (إنشاء وعرض وتحديث)
class AppointmentViewSet(viewsets.ModelViewSet):
    """
    لإنشاء موعد جديد (POST) وعرض وتحديث المواعيد للمستخدم الحالي.
    /api/appointments/
    /api/appointments/{id}/
    /api/appointments/doctors/{doctor_id}/appointments/
    """
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated] # <== يجب أن يكون المستخدم مسجلاً للدخول

    def get_queryset(self):
        """
        عرض المواعيد للمريض أو الطبيب الحالي فقط.
        """
        user = self.request.user
        
        # إذا كان المستخدم مريضاً، أظهر مواعيده
        if hasattr(user, 'userprofile') and user.userprofile.user_type == 'PATIENT':
            return Appointment.objects.filter(patient__user_profile=user.userprofile).order_by('-appointment_date')
        
        # إذا كان المستخدم طبيباً، أظهر مواعيده
        elif hasattr(user, 'userprofile') and user.userprofile.user_type == 'DOCTOR':
            return Appointment.objects.filter(doctor__user_profile=user.userprofile).order_by('-appointment_date')
            
        # للمشرفين، أظهر كل المواعيد
        return Appointment.objects.all().order_by('-appointment_date')

    # =========================================================================
    # 📌 دالة مخصصة لجلب مواعيد طبيب معين (تستخدمها لوحة Flutter)
    # المسار النهائي: /api/appointments/doctors/{doctor_id}/appointments/
    @action(detail=False, methods=['get'], url_path=r'doctors/(?P<doctor_id>\d+)/appointments')
    def doctor_appointments_specific(self, request, doctor_id=None):
        try:
            # التحقق من وجود ملف الطبيب
            doctor_profile = DoctorProfile.objects.get(user_profile__user_id=doctor_id)
            
            # فلترة المواعيد الخاصة بهذا الطبيب فقط
            appointments = Appointment.objects.filter(doctor=doctor_profile).order_by('appointment_date')
            
            serializer = self.get_serializer(appointments, many=True)
            return Response(serializer.data)
        
        except DoctorProfile.DoesNotExist:
            return Response({'error': 'Doctor profile not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    # =========================================================================

    # تخصيص عملية الإنشاء لضمان أن الموعد يتم إنشاؤه بواسطة مريض
    def perform_create(self, serializer):
        user = self.request.user
        if hasattr(user, 'userprofile') and user.userprofile.user_type == 'PATIENT':
            try:
                patient_profile = user.userprofile.patientprofile
                
                # تأكيد أن المريض المُرسل هو المستخدم الحالي (للمزيد من الأمان)
                if serializer.validated_data['patient_id'] != patient_profile.pk:
                    raise permissions.PermissionDenied("You can only book an appointment for yourself.")

                # حفظ الموعد
                serializer.save(patient=patient_profile, status='PENDING')
                
            except AttributeError:
                raise permissions.PermissionDenied("Only patients can book appointments.")
        else:
            raise permissions.PermissionDenied("Only patients can book appointments.")
    
# View لعرض الأطباء المتخصصين في مرض معين
class DoctorsByDiseaseView(generics.ListAPIView):
    """
    عرض الأطباء المتخصصين في مرض معين (عبر ID المرض)
    /api/doctors/by_disease/{disease_id}/
    """
    serializer_class = DoctorProfileSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        disease_id = self.kwargs['disease_id']
        disease = get_object_or_404(Disease, pk=disease_id)
        return DoctorProfile.objects.filter(specialization=disease.specialization)