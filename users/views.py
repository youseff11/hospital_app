from rest_framework import viewsets, generics, permissions, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

# استيراد من نفس المجلد بعد الدمج
from .models import (
    UserProfile, PatientProfile, DoctorProfile, 
    Specialization, Disease, Appointment
)
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer,
    SpecializationSerializer, DiseaseSerializer, 
    AppointmentSerializer, DoctorProfileSerializer
)

# ================================
# 1️⃣ الحسابات (Authentication)
# ================================

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            profile = UserProfile.objects.get(user=user)
            
            # الحصول على الـ profile_id للمريض افتراضياً عند التسجيل
            p_id = profile.patientprofile.pk if hasattr(profile, 'patientprofile') else None

            return Response({
                "message": "User created successfully.",
                "id": user.id,
                "username": user.username,
                "role": profile.user_type,
                "profile_id": p_id,
                "token": token.key
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user is None:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        profile, _ = UserProfile.objects.get_or_create(user=user)
        token, _ = Token.objects.get_or_create(user=user)

        # تحديد الـ ID الخاص بنوع الحساب (دكتور أو مريض)
        p_id = None
        if profile.user_type == 'PATIENT' and hasattr(profile, 'patientprofile'):
            p_id = profile.patientprofile.pk
        elif profile.user_type == 'DOCTOR' and hasattr(profile, 'doctorprofile'):
            p_id = profile.doctorprofile.pk

        return Response({
            'id': user.id,
            'username': user.username,
            'role': profile.user_type,
            'profile_id': p_id,
            'token': token.key,
        }, status=status.HTTP_200_OK)

# ================================
# 2️⃣ الأطباء والتخصصات (Medical Data)
# ================================

class SpecializationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Specialization.objects.all()
    serializer_class = SpecializationSerializer
    permission_classes = [AllowAny]

class DiseaseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Disease.objects.all()
    serializer_class = DiseaseSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name_en', 'name_ar', 'symptoms_en', 'symptoms_ar', 'specialization__name_en','specialization__name_ar']

class DoctorListView(generics.ListAPIView):
    queryset = DoctorProfile.objects.all()
    serializer_class = DoctorProfileSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['user_profile__user__username', 'specialization__name_en']

class DoctorProfileView(generics.RetrieveAPIView):
    serializer_class = DoctorProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_object_or_404(DoctorProfile, user_profile__user=self.request.user)

class DoctorsByDiseaseView(generics.ListAPIView):
    serializer_class = DoctorProfileSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        disease = get_object_or_404(Disease, pk=self.kwargs['disease_id'])
        return DoctorProfile.objects.filter(specialization=disease.specialization)

# ================================
# 3️⃣ المواعيد (Appointments)
# ================================

class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        profile = user.userprofile
        if profile.user_type == 'PATIENT':
            return Appointment.objects.filter(patient__user_profile=profile)
        elif profile.user_type == 'DOCTOR':
            return Appointment.objects.filter(doctor__user_profile=profile)
        return Appointment.objects.all()

    def perform_create(self, serializer):
        profile = self.request.user.userprofile
        if profile.user_type == 'PATIENT':
            serializer.save(patient=profile.patientprofile, status='PENDING')
        else:
            raise permissions.PermissionDenied("Only patients can book.")

# ================================
# 4️⃣ الإدارة (Admin)
# ================================

class AdminListUsers(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        profiles = UserProfile.objects.select_related("user").all()
        data = [{
            "id": p.user.id,
            "username": p.user.username,
            "role": p.user_type,
            "email": p.user.email
        } for p in profiles]
        return Response(data)

class AdminDeleteUser(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        user.delete()
        return Response({"message": "Deleted"})

class AdminUpdateRole(APIView):
    permission_classes = [IsAdminUser]

    def put(self, request, user_id):
        profile = get_object_or_404(UserProfile, user_id=user_id)
        profile.user_type = request.data.get("role")
        profile.save()
        return Response({"message": "Updated"})