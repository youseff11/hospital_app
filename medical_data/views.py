# medical_data/views.py

from rest_framework import viewsets, generics, permissions, filters
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Specialization, Disease, Appointment
from .serializers import (
    SpecializationSerializer, 
    DiseaseSerializer, 
    AppointmentSerializer,
    DoctorProfileSerializer
)
from users.models import DoctorProfile

# 1. ViewSet لعرض التخصصات (كما لديك بالفعل)
class SpecializationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    قائمة تخصصات الأطباء (قراءة فقط)
    /api/specializations/
    """
    queryset = Specialization.objects.all()
    serializer_class = SpecializationSerializer
    permission_classes = [AllowAny] 


# 2. ViewSet لعرض الأمراض (قراءة فقط)
class DiseaseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    قائمة الأمراض وتفاصيلها (قراءة فقط)
    /api/diseases/
    """
    queryset = Disease.objects.all()
    serializer_class = DiseaseSerializer
    permission_classes = [AllowAny]
    # يمكن إضافة مرشحات البحث بناءً على اسم المرض أو التخصص
    filter_backends = [filters.SearchFilter]
    search_fields = ['name_ar', 'specialization__name_ar']


# 3. View لعرض قائمة الأطباء (للبحث والحجز)
class DoctorListView(generics.ListAPIView):
    """
    قائمة الأطباء مع إمكانية البحث حسب التخصص
    /api/doctors/
    """
    queryset = DoctorProfile.objects.all()
    serializer_class = DoctorProfileSerializer
    permission_classes = [AllowAny]
    
    # يمكن السماح بالبحث عن طبيب حسب التخصص
    filter_backends = [filters.SearchFilter]
    # يتيح البحث باستخدام: /api/doctors/?search=قلب
    search_fields = ['user_profile__user__username', 'specialization__name_ar']


# 4. ViewSet لإدارة المواعيد (إنشاء وعرض)
class AppointmentViewSet(viewsets.ModelViewSet):
    """
    لإنشاء موعد جديد (POST) وعرض المواعيد للمستخدم الحالي (GET)
    /api/appointments/
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

    # تخصيص عملية الإنشاء لضمان أن الموعد يتم إنشاؤه بواسطة مريض
    def perform_create(self, serializer):
        user = self.request.user
        if hasattr(user, 'userprofile') and user.userprofile.user_type == 'PATIENT':
            # يجب أن يكون حقل patient_id في الـ serializer متطابقاً مع المستخدم الحالي
            # (هذا يزيد من الأمان)
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
    
class DoctorsByDiseaseView(generics.ListAPIView):
    """
    عرض الأطباء المتخصصين في مرض معين (عبر ID المرض)
    /api/doctors/by_disease/{disease_id}/
    """
    serializer_class = DoctorProfileSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        # 1. جلب ID المرض من الـ URL
        disease_id = self.kwargs['disease_id']
        
        # 2. البحث عن المرض
        disease = get_object_or_404(Disease, pk=disease_id)
        
        # 3. إرجاع الأطباء الذين تخصصهم يطابق تخصص المرض
        return DoctorProfile.objects.filter(specialization=disease.specialization)