from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    UserProfile, 
    PatientProfile, 
    DoctorProfile, 
    Specialization, 
    Disease, 
    Appointment
)

# 1. بروفايل الطبيب (تمت إضافة جلب بيانات التخصص باللغتين)
class DoctorProfileSerializer(serializers.ModelSerializer):
    # نرسل الـ id الحقيقي للمستخدم لسهولة التعامل في Flutter
    id = serializers.IntegerField(source='user_profile.user.id', read_only=True)
    full_name = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()
    
    # التعديل الجديد: جلب بيانات التخصص كاملة (عربي وإنجليزي)
    specialization_data = serializers.SerializerMethodField()

    class Meta:
        model = DoctorProfile
        fields = [
            'id', 
            'full_name', 
            'phone_number', 
            'rating', 
            'license_number',
            'specialization_data' # الحقل الجديد
        ]

    def get_specialization_data(self, obj):
        if obj.specialization:
            return {
                "name_en": obj.specialization.name_en,
                "name_ar": obj.specialization.name_ar
            }
        return {"name_en": "General", "name_ar": "عام"}

    def get_full_name(self, obj):
        try:
            return obj.user_profile.user.username
        except:
            return "Unknown"

    def get_phone_number(self, obj):
        try:
            return obj.user_profile.phone_number
        except:
            return "N/A"

# 2. Serializer التخصصات
class SpecializationSerializer(serializers.ModelSerializer):
    # جلب قائمة الأطباء المرتبطين بهذا التخصص مباشرة
    doctors = DoctorProfileSerializer(source='doctorprofile_set', many=True, read_only=True)

    class Meta:
        model = Specialization
        fields = ['id', 'name_en','name_ar', 'description_en', 'icon', 'doctors']

# 3. Serializer تسجيل المستخدمين
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    phone_number = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'phone_number')

    def create(self, validated_data):
        phone_number = validated_data.pop('phone_number')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        profile = UserProfile.objects.create(
            user=user,
            user_type='PATIENT',
            phone_number=phone_number
        )
        PatientProfile.objects.create(user_profile=profile)
        return user

# 4. Serializer تسجيل الدخول
class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

# 5. Serializer الأمراض
class DiseaseSerializer(serializers.ModelSerializer):
    specialization_name = serializers.CharField(source='specialization.name_en', read_only=True)

    class Meta:
        model = Disease
        fields = [
            'id', 
            'name_ar', 
            'name_en', 
            'symptoms_ar', 
            'symptoms_en', 
            'specialization_name'
        ]

# 6. Serializer المواعيد
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