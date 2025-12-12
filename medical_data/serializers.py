from rest_framework import serializers
from .models import Specialization, Disease, Appointment
from users.models import DoctorProfile, PatientProfile 


# 1. Serializer لعرض بيانات التخصص
class SpecializationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialization
        fields = ['id', 'name_en', 'description_en', 'icon']


# 2. Serializer لعرض بيانات الطبيب
class DoctorProfileSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='user_profile_id', read_only=True)

    specialization = SpecializationSerializer(read_only=True)
    username = serializers.CharField(source='user_profile.user.username', read_only=True)
    full_name = serializers.CharField(source='user_profile.user.get_full_name', read_only=True)

    class Meta:
        model = DoctorProfile
        fields = ['id', 'username', 'full_name', 'specialization', 'rating', 'license_number']


# 3. Serializer لعرض بيانات المرض
class DiseaseSerializer(serializers.ModelSerializer):
    specialization_name = serializers.CharField(source='specialization.name_en', read_only=True)

    class Meta:
        model = Disease
        fields = ['id', 'name_en', 'specialization_name', 'symptoms']


# 4. Serializer لحجز الموعد
class AppointmentSerializer(serializers.ModelSerializer):
    patient_id = serializers.IntegerField(write_only=True)
    doctor_id = serializers.IntegerField(write_only=True)

    patient_name = serializers.CharField(source='patient.user_profile.user.username', read_only=True)
    doctor_name = serializers.CharField(source='doctor.user_profile.user.username', read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'id', 'patient_id', 'doctor_id', 'appointment_date',
            'status', 'notes', 'patient_name', 'doctor_name'
        ]
        read_only_fields = ['status']

    def create(self, validated_data):
        patient_id = validated_data.pop('patient_id')
        doctor_id = validated_data.pop('doctor_id')

        try:
            patient = PatientProfile.objects.get(pk=patient_id)
            doctor = DoctorProfile.objects.get(pk=doctor_id)
        except (PatientProfile.DoesNotExist, DoctorProfile.DoesNotExist):
            raise serializers.ValidationError(
                {"detail": "Invalid patient or doctor ID provided."}
            )

        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            **validated_data
        )
        return appointment
