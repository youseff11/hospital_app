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

# 1. بروفايل الطبيب
class DoctorProfileSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='user_profile.user.id', read_only=True)
    full_name = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()
    specialization_data = serializers.SerializerMethodField()

    class Meta:
        model = DoctorProfile
        fields = [
            'id', 
            'full_name', 
            'phone_number', 
            'rating', 
            'license_number',
            'specialization_data'
        ]

    def get_specialization_data(self, obj):
        if obj.specialization:
            return {
                "name_en": obj.specialization.name_en,
                "name_ar": obj.specialization.name_ar
            }
        return {"name_en": "General", "name_ar": "عام"}

    def get_full_name(self, obj):
        try: return obj.user_profile.user.username
        except: return "Unknown"

    def get_phone_number(self, obj):
        try: return obj.user_profile.phone_number
        except: return "N/A"

# 2. Serializer التخصصات
class SpecializationSerializer(serializers.ModelSerializer):
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

# 5. Serializer الأمراض (تم التعديل لترجمة التخصص)
class DiseaseSerializer(serializers.ModelSerializer):
    # حقول للقراءة فقط لعرض الأسماء في Flutter
    specialization_name_ar = serializers.CharField(source='specialization.name_ar', read_only=True)
    specialization_name_en = serializers.CharField(source='specialization.name_en', read_only=True)

    class Meta:
        model = Disease
        fields = [
            'id', 
            'name_ar', 
            'name_en', 
            'symptoms_ar', 
            'symptoms_en', 
            'specialization',         # أضفنا هذا الحقل لاستقبال الـ ID من التطبيق
            'specialization_name_ar', 
            'specialization_name_en'
        ]
        # لجعل التخصص اختيارياً أو التأكد من التعامل معه
        extra_kwargs = {
            'specialization': {'required': False, 'allow_null': True}
        }

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

# 7 بروفايل المريض
class PatientProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user_profile.user.username', read_only=True)
    phone_number = serializers.CharField(source='user_profile.phone_number', read_only=True)
    address = serializers.CharField(source='user_profile.address', read_only=True)
    
    # إضافة هذا الحقل ضروري جداً لأن كود فلاتر يبحث عنه للفلترة
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = PatientProfile
        fields = [
            'user_profile_id', 
            'full_name', 
            'phone_number', 
            'address',
            'date_of_birth', 
            'blood_group', 
            'medical_history', # تأكد أن هذا الحقل موجود هنا ليظهر في التطبيق
            'user_details'     # الحقل الجديد لربط الهوية
        ]

    # دالة لجلب بيانات المستخدم لضمان عدم حدوث خطأ "null" في فلاتر
    def get_user_details(self, obj):
        return {
            "username": obj.user_profile.user.username,
            "email": obj.user_profile.user.email
        }