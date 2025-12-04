# users/serializers.py (الكود المعدل)

from rest_framework import serializers
from django.contrib.auth.models import User
# 🌟 استيراد UserProfile فقط، لنعدل الوصول للمتغير بداخله
from .models import UserProfile, PatientProfile, DoctorProfile 
from django.contrib.auth import get_user_model

# Serializer لإنشاء مستخدم جديد
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    # 🌟 الوصول إلى المتغير من خلال اسم الكلاس: UserProfile.USER_TYPE_CHOICES
    user_type = serializers.ChoiceField(choices=UserProfile.USER_TYPE_CHOICES) 
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'user_type') # إضافة user_type هنا
        
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
            DoctorProfile.objects.create(user_profile=profile, specialization="General") # يمكن تحديد تخصص افتراضي
        
        return user

# Serializer لإرجاع نوع المستخدم عند الدخول (لا يحتاج لتعديل كبير هنا)
class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    # لا داعي لإضافة user_type هنا، لأنه يتم إرجاعه في الـ View مباشرة