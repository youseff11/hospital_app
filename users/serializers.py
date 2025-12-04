# users/serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, PatientProfile, DoctorProfile
from medical_data.models import Specialization


# =============================
# 1️⃣ User Registration
# =============================
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        # دائماً PATIENT تلقائي
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )

        # إنشاء UserProfile
        profile = UserProfile.objects.create(
            user=user,
            user_type='PATIENT'
        )

        # إنشاء PatientProfile تلقائياً
        PatientProfile.objects.create(user_profile=profile)

        return user


# =============================
# 2️⃣ User Login
# =============================
class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
