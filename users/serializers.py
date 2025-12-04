# users/serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, PatientProfile, DoctorProfile 
from medical_data.models import Specialization # <== استيراد نموذج التخصص
from django.contrib.auth import get_user_model


# Serializer لإنشاء مستخدم جديد (معدّل)
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    user_type = serializers.ChoiceField(choices=UserProfile.USER_TYPE_CHOICES) 
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'user_type') 
        
    def create(self, validated_data):
        # فصل حقل user_type قبل إنشاء مستخدم Django
        user_type = validated_data.pop('user_type', 'PATIENT') 

        # إنشاء مستخدم Django الأساسي
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        # إنشاء UserProfile وتحديد نوع المستخدم
        profile = UserProfile.objects.create(
            user=user,
            user_type=user_type
        )
        
        # إنشاء Profile الإضافي بناءً على النوع
        if user_type == 'PATIENT':
            PatientProfile.objects.create(user_profile=profile)
            
        elif user_type == 'DOCTOR':
            # التعامل مع Foreign Key للتخصص
            default_specialization = Specialization.objects.first() # <== تعديل مهم
            
            # ملاحظة: إذا لم يكن هناك أي تخصص في قاعدة البيانات، يجب أن يترك الحقل فارغاً إذا كان مسموحاً (null=True)
            if not default_specialization and DoctorProfile._meta.get_field('specialization').null:
                 DoctorProfile.objects.create(user_profile=profile)
            elif default_specialization:
                DoctorProfile.objects.create(
                    user_profile=profile, 
                    specialization=default_specialization # تمرير الكائن
                )
            
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)