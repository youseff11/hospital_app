from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, PatientProfile, DoctorProfile


# =============================
# 1️⃣ User Registration
# =============================
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    phone_number = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'phone_number')

    def create(self, validated_data):
        phone_number = validated_data.pop('phone_number')

        # إنشاء المستخدم
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )

        # إنشاء UserProfile + حفظ رقم التليفون
        profile = UserProfile.objects.create(
            user=user,
            user_type='PATIENT',
            phone_number=phone_number
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
