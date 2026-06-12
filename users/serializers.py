from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    UserProfile, 
    PatientProfile, 
    DoctorProfile, 
    Specialization, 
    Disease, 
    Appointment,
    Prescription,
    PrescriptionMedicine
)

# 1. Doctor Profile Serializer
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
        try:
            user = obj.user_profile.user
            return user.get_full_name() if user.get_full_name() else user.username
        except:
            return "Unknown"

    def get_phone_number(self, obj):
        try:
            return obj.user_profile.phone_number
        except:
            return "N/A"

# 2. Specialization Serializer
class SpecializationSerializer(serializers.ModelSerializer):
    doctors = DoctorProfileSerializer(source='doctorprofile_set', many=True, read_only=True)

    class Meta:
        model = Specialization
        fields = ['id', 'name_en','name_ar', 'description_en', 'icon', 'doctors']

# 3. User Registration Serializer
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

# 4. User Login Serializer
class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

# 5. Disease Serializer
class DiseaseSerializer(serializers.ModelSerializer):
    specialization_name_ar = serializers.CharField(source='specialization.name_ar', read_only=True)
    specialization_name_en = serializers.CharField(source='specialization.name_en', read_only=True)

    class Meta:
        model = Disease
        fields = [
            'id', 'name_ar', 'name_en', 'symptoms_ar', 'symptoms_en', 
            'specialization', 'specialization_name_ar', 'specialization_name_en'
        ]
        extra_kwargs = {'specialization': {'required': False, 'allow_null': True}}

# 6. Appointment Serializer
class AppointmentSerializer(serializers.ModelSerializer):
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=PatientProfile.objects.all(), source='patient', write_only=True
    )
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=DoctorProfile.objects.all(), source='doctor', write_only=True
    )
    patient_name = serializers.CharField(source='patient.user_profile.user.username', read_only=True)
    doctor_name = serializers.CharField(source='doctor.user_profile.user.username', read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'id', 'patient_id', 'doctor_id', 'appointment_date', 
            'status', 'notes', 'patient_name', 'doctor_name'
        ]
        read_only_fields = ['patient_name', 'doctor_name']

# 7. Patient Profile Serializer
class PatientProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user_profile.user.username', read_only=True)
    phone_number = serializers.CharField(source='user_profile.phone_number', read_only=True)
    address = serializers.CharField(source='user_profile.address', read_only=True)
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = PatientProfile
        fields = [
            'user_profile_id', 'full_name', 'phone_number', 'address',
            'date_of_birth', 'blood_group', 'medical_history', 'user_details'
        ]

    def get_user_details(self, obj):
        return {
            "username": obj.user_profile.user.username,
            "email": obj.user_profile.user.email
        }

# 8. Prescription Medicine Serializer
class PrescriptionMedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrescriptionMedicine
        fields = ['id', 'medicine_name', 'dosage', 'duration', 'instructions']
        extra_kwargs = {
            'instructions': {'required': False, 'allow_blank': True, 'allow_null': True},
            'dosage': {'required': False, 'allow_blank': True},
            'duration': {'required': False, 'allow_blank': True},
        }

# 9. Prescription Serializer (المتوافق مع تعدد الروشتات)
class PrescriptionSerializer(serializers.ModelSerializer):
    medicines = PrescriptionMedicineSerializer(many=True)
    patient_name = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()
    appointment_date = serializers.DateTimeField(source='appointment.appointment_date', read_only=True)

    class Meta:
        model = Prescription
        fields = [
            'id', 'appointment', 'diagnosis', 'medicines', 
            'patient_name', 'doctor_name', 'appointment_date', 'created_at'
        ]

    def get_patient_name(self, obj):
        try:
            user = obj.appointment.patient.user_profile.user
            return user.get_full_name() if user.get_full_name() else user.username
        except:
            return "Unknown Patient"

    def get_doctor_name(self, obj):
        try:
            user = obj.appointment.doctor.user_profile.user
            return user.get_full_name() if user.get_full_name() else user.username
        except:
            return "Dr. Unknown"

    def create(self, validated_data):
        medicines_data = validated_data.pop('medicines', [])
        # إنشاء الروشتة - الآن ForeignKey سيسمح بإنشاء سجلات متعددة لنفس الموعد
        prescription = Prescription.objects.create(**validated_data)
        
        for medicine_data in medicines_data:
            PrescriptionMedicine.objects.create(prescription=prescription, **medicine_data)
        return prescription

    def update(self, instance, validated_data):
        medicines_data = validated_data.pop('medicines', None)
        instance.diagnosis = validated_data.get('diagnosis', instance.diagnosis)
        # ملاحظة: إذا تم تحديث الـ appointment، سيتم قبوله هنا أيضاً
        instance.appointment = validated_data.get('appointment', instance.appointment)
        instance.save()

        if medicines_data is not None:
            # مسح الأدوية القديمة وإضافة الجديدة المرتبطة بهذه الروشتة تحديداً
            instance.medicines.all().delete()
            for medicine_data in medicines_data:
                PrescriptionMedicine.objects.create(prescription=instance, **medicine_data)
        
        return instance