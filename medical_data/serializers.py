from rest_framework import serializers
from .models import Specialization, Disease, Appointment
from users.models import DoctorProfile

# 1. Serializer لعرض بيانات التخصص
class SpecializationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialization
        fields = ['id', 'name_ar', 'description_ar', 'icon']

# 2. Serializer لعرض بيانات الطبيب
class DoctorProfileSerializer(serializers.ModelSerializer):
    # نستخدم حقل الـ User الأساسي للحصول على الاسم والبريد الإلكتروني
    username = serializers.CharField(source='user_profile.user.username', read_only=True)
    full_name = serializers.CharField(source='user_profile.user.get_full_name', read_only=True)
    
    class Meta:
        model = DoctorProfile
        # نضمّن بيانات المستخدم الأساسية بالإضافة لبيانات الطبيب
        fields = ['id', 'username', 'full_name', 'specialization', 'rating'] 

# 3. Serializer لعرض بيانات المرض
class DiseaseSerializer(serializers.ModelSerializer):
    # عرض اسم التخصص المرتبط بدلاً من ID
    specialization_name = serializers.CharField(source='specialization.name_ar', read_only=True)
    
    class Meta:
        model = Disease
        fields = ['id', 'name_ar', 'specialization_name', 'symptoms']

# 4. Serializer لحجز الموعد
class AppointmentSerializer(serializers.ModelSerializer):
    # هذه الحقول ضرورية للإدخال
    patient_id = serializers.IntegerField(write_only=True)
    doctor_id = serializers.IntegerField(write_only=True)
    
    # هذه الحقول للعرض فقط
    patient_name = serializers.CharField(source='patient.user_profile.user.username', read_only=True)
    doctor_name = serializers.CharField(source='doctor.user_profile.user.username', read_only=True)
    
    class Meta:
        model = Appointment
        fields = ['id', 'patient_id', 'doctor_id', 'appointment_date', 'status', 'notes', 'patient_name', 'doctor_name']
        read_only_fields = ['status']