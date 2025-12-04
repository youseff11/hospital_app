# medical_data/serializers.py

from rest_framework import serializers
from .models import Specialization, Disease, Appointment
# نستورد DoctorProfile و PatientProfile للتحقق عند إنشاء الموعد
from users.models import DoctorProfile, PatientProfile 


# 1. Serializer لعرض بيانات التخصص
class SpecializationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialization
        fields = ['id', 'name_ar', 'description_ar', 'icon']


# 2. Serializer لعرض بيانات الطبيب (معدّل)
class DoctorProfileSerializer(serializers.ModelSerializer):
    # تضمين Serializer التخصص لعرض البيانات كاملة (Nested Serializer)
    specialization = SpecializationSerializer(read_only=True) # <== تعديل مهم

    # نستخدم حقل الـ User الأساسي للحصول على الاسم والبريد الإلكتروني
    username = serializers.CharField(source='user_profile.user.username', read_only=True)
    full_name = serializers.CharField(source='user_profile.user.get_full_name', read_only=True)
    
    class Meta:
        model = DoctorProfile
        # نضمن بيانات المستخدم الأساسية بالإضافة لبيانات الطبيب
        fields = ['id', 'username', 'full_name', 'specialization', 'rating', 'license_number'] 


# 3. Serializer لعرض بيانات المرض
class DiseaseSerializer(serializers.ModelSerializer):
    # عرض اسم التخصص المرتبط بدلاً من ID
    specialization_name = serializers.CharField(source='specialization.name_ar', read_only=True)
    
    class Meta:
        model = Disease
        fields = ['id', 'name_ar', 'specialization_name', 'symptoms']

# 4. Serializer لحجز الموعد (معدّل)
class AppointmentSerializer(serializers.ModelSerializer):
    # هذه الحقول ضرورية للإدخال (يتم إرسالها من Flutter)
    patient_id = serializers.IntegerField(write_only=True)
    doctor_id = serializers.IntegerField(write_only=True)
    
    # هذه الحقول للعرض فقط (يتم إرسالها إلى Flutter)
    patient_name = serializers.CharField(source='patient.user_profile.user.username', read_only=True)
    doctor_name = serializers.CharField(source='doctor.user_profile.user.username', read_only=True)
    
    class Meta:
        model = Appointment
        fields = ['id', 'patient_id', 'doctor_id', 'appointment_date', 'status', 'notes', 'patient_name', 'doctor_name']
        read_only_fields = ['status'] 
        
    def create(self, validated_data):
        # 1. استخراج IDs من البيانات المدخلة وحذفها من validated_data
        patient_id = validated_data.pop('patient_id')
        doctor_id = validated_data.pop('doctor_id')

        # 2. تحويل IDs إلى كائنات النماذج
        try:
            # يجب أن يكون الـ ID الموجود هو Primary Key لنموذج PatientProfile/DoctorProfile
            patient = PatientProfile.objects.get(pk=patient_id)
            doctor = DoctorProfile.objects.get(pk=doctor_id)
        except (PatientProfile.DoesNotExist, DoctorProfile.DoesNotExist):
            raise serializers.ValidationError({"detail": "Invalid patient or doctor ID provided."})

        # 3. إنشاء الموعد باستخدام الكائنات
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            **validated_data
        )
        return appointment