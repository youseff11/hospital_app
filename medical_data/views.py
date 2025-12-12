# medical_data/views.py

from rest_framework import viewsets, generics, permissions, filters, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Specialization, Disease, Appointment
from .serializers import (
    SpecializationSerializer, 
    DiseaseSerializer, 
    AppointmentSerializer,
    DoctorProfileSerializer
)
from users.models import DoctorProfile, UserProfile, PatientProfile


# 1. ViewSet لعرض التخصصات
class SpecializationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Specialization.objects.all()
    serializer_class = SpecializationSerializer
    permission_classes = [AllowAny]


# 2. ViewSet لعرض الأمراض
class DiseaseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Disease.objects.all()
    serializer_class = DiseaseSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name_en', 'specialization__name_en']


# 3. View لعرض قائمة الأطباء
class DoctorListView(generics.ListAPIView):
    queryset = DoctorProfile.objects.all()
    serializer_class = DoctorProfileSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['user_profile__user__username', 'specialization__name_en']


# 4. Appointment ViewSet
class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # لو مريض → هات مواعيده فقط
        if hasattr(user, 'userprofile') and user.userprofile.user_type == 'PATIENT':
            return Appointment.objects.filter(
                patient__user_profile=user.userprofile
            ).order_by('-appointment_date')

        # لو طبيب → هات مواعيده فقط
        elif hasattr(user, 'userprofile') and user.userprofile.user_type == 'DOCTOR':
            return Appointment.objects.filter(
                doctor__user_profile=user.userprofile
            ).order_by('-appointment_date')

        # لو Admin رجّع كل المواعيد
        return Appointment.objects.all().order_by('-appointment_date')

    @action(detail=False, methods=['get'], url_path=r'doctors/(?P<doctor_id>\d+)/appointments')
    def doctor_appointments_specific(self, request, doctor_id=None):
        try:
            doctor_profile = DoctorProfile.objects.get(user_profile__user_id=doctor_id)
            appointments = Appointment.objects.filter(
                doctor=doctor_profile
            ).order_by('appointment_date')

            serializer = self.get_serializer(appointments, many=True)
            return Response(serializer.data)

        except DoctorProfile.DoesNotExist:
            return Response({'error': 'Doctor profile not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def perform_create(self, serializer):
        user = self.request.user

        if hasattr(user, 'userprofile') and user.userprofile.user_type == 'PATIENT':
            patient_profile = user.userprofile.patientprofile

            # أمن إضافي: تأكد إن المستخدم بيحجز لنفسه
            if serializer.validated_data['patient_id'] != patient_profile.pk:
                raise permissions.PermissionDenied("You can only book an appointment for yourself.")

            serializer.save(patient=patient_profile, status='PENDING')

        else:
            raise permissions.PermissionDenied("Only patients can book appointments.")


# 5. View لعرض الأطباء المتخصصين في مرض معيّن
class DoctorsByDiseaseView(generics.ListAPIView):
    serializer_class = DoctorProfileSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        disease_id = self.kwargs['disease_id']
        disease = get_object_or_404(Disease, pk=disease_id)
        return DoctorProfile.objects.filter(specialization=disease.specialization)
