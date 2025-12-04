# users/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import authenticate
from .serializers import UserRegistrationSerializer, UserLoginSerializer
from .models import UserProfile, PatientProfile, DoctorProfile
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from medical_data.serializers import DoctorProfileSerializer
from rest_framework.authtoken.models import Token


# ================================
# 1️⃣  Register (Sign Up)
# ================================
class RegisterView(APIView):
    """
    POST /api/users/register/
    - يتوقع: username, email, password (حسب الserializer لديك)
    - يعيد: message, id, username, role, profile_id, token
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # إنشاء توكن للمستخدم الجديد أو الحصول عليه
            token, created = Token.objects.get_or_create(user=user)

            # الحصول على ال UserProfile (يفترض وجوده بواسطة signal)
            try:
                profile = UserProfile.objects.get(user=user)
            except UserProfile.DoesNotExist:
                # كحل احترازي - إنشاؤه لو لم يكن موجودًا
                profile = UserProfile.objects.create(user=user, user_type='PATIENT')

            # تحديد profile_id حسب نوع المستخدم (patient/doctor)
            profile_id = None
            if profile.user_type == 'PATIENT':
                try:
                    profile_id = profile.patientprofile.pk
                except PatientProfile.DoesNotExist:
                    # أنشئ PatientProfile احتياطياً
                    patient = PatientProfile.objects.create(user_profile=profile)
                    profile_id = patient.pk
            elif profile.user_type == 'DOCTOR':
                try:
                    profile_id = profile.doctorprofile.pk
                except DoctorProfile.DoesNotExist:
                    # إذا لم يكن موجودًا، ضع None أو أنشئ واحد حسب سياستك
                    profile_id = None

            return Response({
                "message": "User created successfully.",
                "id": user.id,
                "username": user.username,
                "role": profile.user_type,
                "profile_id": profile_id,
                "token": token.key
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ================================
# 2️⃣  Login
# ================================
class LoginView(APIView):
    """
    POST /api/users/login/
    - يتوقع: username, password
    - يعيد: id, username, role, profile_id, token
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        if user is None:
            return Response({'error': 'Invalid username or password.'},
                            status=status.HTTP_401_UNAUTHORIZED)

        # الحصول على ال profile والtoken
        try:
            profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            # حالة نادرة: إنشاؤه تلقائياً
            profile = UserProfile.objects.create(user=user, user_type='PATIENT')

        token, created = Token.objects.get_or_create(user=user)

        # حساب profile_id بناءً على النوع
        profile_id = None
        if profile.user_type == 'PATIENT':
            try:
                profile_id = profile.patientprofile.pk
            except PatientProfile.DoesNotExist:
                profile_id = None
        elif profile.user_type == 'DOCTOR':
            try:
                profile_id = profile.doctorprofile.pk
            except DoctorProfile.DoesNotExist:
                profile_id = None
        else:
            # ADMIN أو أنواع أخرى: profile_id يبقى None
            profile_id = None

        return Response({
            'id': user.id,
            'username': user.username,
            'role': profile.user_type,
            'profile_id': profile_id,
            'token': token.key,
        }, status=status.HTTP_200_OK)


# ================================
# 3️⃣  Doctor Profile (current doctor)
# ================================
class DoctorProfileView(RetrieveAPIView):
    """
    GET /api/users/doctors/me/
    - يعيد بروفايل الدكتور المسجل دخوله
    - يتطلب توكن Authentication
    """
    serializer_class = DoctorProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # التحقق أن المستخدم هو DOCTOR
        try:
            user_profile = self.request.user.userprofile
        except UserProfile.DoesNotExist:
            raise permissions.PermissionDenied("User profile not found.")

        if user_profile.user_type != 'DOCTOR':
            raise permissions.PermissionDenied("You are not authorized to view this profile.")

        try:
            return user_profile.doctorprofile
        except DoctorProfile.DoesNotExist:
            raise permissions.PermissionDenied("Doctor profile not found.")
# ================================
# 4️⃣  Admin - List Users
# ================================
class AdminListUsers(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        users = UserProfile.objects.select_related("user").all()

        data = []
        for p in users:
            data.append({
                "id": p.user.id,
                "username": p.user.username,
                "email": p.user.email,
                "role": p.user_type,
                "profile_id": (
                    p.patientprofile.id if p.user_type == "PATIENT"
                    else p.doctorprofile.id if p.user_type == "DOCTOR"
                    else None
                ),
            })

        return Response(data, status=status.HTTP_200_OK)
# ================================
# 5️⃣  Admin - Delete User
# ================================
class AdminDeleteUser(APIView):
    permission_classes = [permissions.IsAdminUser]

    def delete(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return Response({"message": "User deleted successfully."},
                            status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found."},
                            status=status.HTTP_404_NOT_FOUND)
# ================================
# 6️⃣  Admin - Update User Role
# ================================
class AdminUpdateRole(APIView):
    permission_classes = [permissions.IsAdminUser]

    def put(self, request, user_id):
        new_role = request.data.get("role")

        if new_role not in ["PATIENT", "DOCTOR", "ADMIN"]:
            return Response({"error": "Invalid role."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            user_profile = UserProfile.objects.get(user_id=user_id)
        except UserProfile.DoesNotExist:
            return Response({"error": "User profile not found."},
                            status=status.HTTP_404_NOT_FOUND)

        # تحديث الدور
        user_profile.user_type = new_role
        user_profile.save()

        return Response({
            "message": "Role updated successfully.",
            "new_role": new_role
        }, status=status.HTTP_200_OK)
