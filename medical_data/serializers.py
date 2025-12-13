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
    id = serializers.IntegerField(read_only=True)

    specialization = SpecializationSerializer(read_only=True)
    username = serializers.CharField(
        source='user_profile.user.username',
        read_only=True
    )
    full_name = serializers.CharField(
        source='user_profile.user.get_full_name',
        read_only=True
    )
    phone_number = serializers.CharField(
        source='user_profile.phone_number',
        read_only=True
    )

    class Meta:
        model = DoctorProfile
        fields = [
            'id',
            'username',
            'full_name',
            'specialization',
            'phone_number',
            'rating',
            'license_number',
        ]


# 3. ✅ Disease Serializer (المهم)
class DiseaseSerializer(serializers.ModelSerializer):
    # توافق مع Flutter
    name_ar = serializers.CharField(source='name_en', read_only=True)
    description = serializers.CharField(source='symptoms', read_only=True)
    specialization_name = serializers.CharField(
        source='specialization.name_en',
        read_only=True
    )

    class Meta:
        model = Disease
        fields = [
            'id',
            'name_ar',
            'description',
            'specialization_name'
        ]


# 4. Serializer لحجز الموعد
class AppointmentSerializer(serializers.ModelSerializer):
    patient_id = serializers.IntegerField(write_only=True)
    doctor_id = serializers.IntegerField(write_only=True)

    patient_name = serializers.CharField(
        source='patient.user_profile.user.username',
        read_only=True
    )
    doctor_name = serializers.CharField(
        source='doctor.user_profile.user.username',
        read_only=True
    )

    class Meta:
        model = Appointment
        fields = [
            'id',
            'patient_id',
            'doctor_id',
            'appointment_date',
            'status',
            'notes',
            'patient_name',
            'doctor_name'
        ]
        read_only_fields = ['status']
