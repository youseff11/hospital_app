# users/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from .serializers import UserRegistrationSerializer, UserLoginSerializer
from .models import UserProfile
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from medical_data.serializers import DoctorProfileSerializer
from rest_framework.authtoken.models import Token

class RegisterView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User created successfully.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        if user is None:
            return Response({'error': 'Invalid username or password.'}, status=status.HTTP_401_UNAUTHORIZED)

        # جلب البروفايل
        profile = UserProfile.objects.get(user=user)

        # الحصول على التوكن أو إنشائه
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'id': user.id,
            'username': user.username,
            'role': profile.user_type,
            'token': token.key,
        }, status=status.HTTP_200_OK)

class DoctorProfileView(RetrieveAPIView):
    """
    عرض بروفايل الطبيب الحالي (المسجل دخوله)
    /api/doctors/me/
    """
    serializer_class = DoctorProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # البحث عن DoctorProfile المرتبط بالمستخدم الحالي
        if self.request.user.userprofile.user_type == 'DOCTOR':
            return self.request.user.userprofile.doctorprofile
        else:
            raise permissions.PermissionDenied("You are not authorized to view this profile.")