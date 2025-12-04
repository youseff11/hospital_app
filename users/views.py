# users/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import authenticate
from .serializers import UserRegistrationSerializer, UserLoginSerializer
from .models import UserProfile
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from medical_data.serializers import DoctorProfileSerializer
from rest_framework.authtoken.models import Token


# ================================
# 1️⃣  Register (Sign Up)
# ================================
class RegisterView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # إنشاء توكن للمستخدم الجديد
            token, created = Token.objects.get_or_create(user=user)

            profile = UserProfile.objects.get(user=user)

            return Response({
                "message": "User created successfully.",
                "id": user.id,
                "username": user.username,
                "role": profile.user_type,   # دائماً PATIENT
                "token": token.key
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ================================
# 2️⃣  Login
# ================================
class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        if user is None:
            return Response({'error': 'Invalid username or password.'},
                            status=status.HTTP_401_UNAUTHORIZED)

        profile = UserProfile.objects.get(user=user)

        # الحصول على التوكن أو إنشائه
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'id': user.id,
            'username': user.username,
            'role': profile.user_type,
            'token': token.key,
        }, status=status.HTTP_200_OK)


# ================================
# 3️⃣  Doctor Profile
# ================================
class DoctorProfileView(RetrieveAPIView):
    """
    عرض بروفايل الطبيب الحالي (المسجل دخوله)
    /api/users/doctors/me/
    """
    serializer_class = DoctorProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):

        # لازم يكون دكتور
        if self.request.user.userprofile.user_type != 'DOCTOR':
            raise permissions.PermissionDenied("You are not authorized to view this profile.")

        return self.request.user.userprofile.doctorprofile
