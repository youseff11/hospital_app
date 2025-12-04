# users/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .serializers import UserRegistrationSerializer
from .models import UserProfile, PatientProfile, DoctorProfile
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from medical_data.serializers import DoctorProfileSerializer
from rest_framework.authtoken.models import Token
from .permissions import IsRealAdmin


# ================================
# 1️⃣ Register
# ================================
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            # Create token
            token, created = Token.objects.get_or_create(user=user)

            # Ensure profile exists
            profile, created_profile = UserProfile.objects.get_or_create(user=user)

            # Assign profile_id
            profile_id = None

            if profile.user_type == 'PATIENT':
                patient, _ = PatientProfile.objects.get_or_create(user_profile=profile)
                profile_id = patient.id

            elif profile.user_type == 'DOCTOR':
                try:
                    profile_id = profile.doctorprofile.id
                except:
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
# 2️⃣ Login
# ================================
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)

        if not user:
            return Response({"error": "Invalid credentials."},
                            status=status.HTTP_401_UNAUTHORIZED)

        token, _ = Token.objects.get_or_create(user=user)

        # Get profile
        profile, _ = UserProfile.objects.get_or_create(user=user)

        # Setup profile_id
        profile_id = None

        if profile.user_type == "PATIENT":
            try:
                profile_id = profile.patientprofile.id
            except:
                profile_id = None

        elif profile.user_type == "DOCTOR":
            try:
                profile_id = profile.doctorprofile.id
            except:
                profile_id = None

        return Response({
            "id": user.id,
            "username": user.username,
            "role": profile.user_type,
            "profile_id": profile_id,
            "token": token.key
        }, status=200)


# ================================
# 3️⃣ Doctor Profile
# ================================
class DoctorProfileView(RetrieveAPIView):
    serializer_class = DoctorProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profile = self.request.user.userprofile

        if profile.user_type != "DOCTOR":
            raise permissions.PermissionDenied("Not a doctor.")

        return profile.doctorprofile


# ================================
# 4️⃣ Admin – List Users
# ================================
class AdminListUsers(APIView):
    permission_classes = [IsRealAdmin]

    def get(self, request):
        users = UserProfile.objects.select_related("user").all()

        data = []
        for u in users:
            data.append({
                "id": u.user.id,
                "username": u.user.username,
                "email": u.user.email,
                "role": u.user_type,
                "profile_id":
                    u.patientprofile.id if u.user_type == "PATIENT" else
                    u.doctorprofile.id if u.user_type == "DOCTOR" else None
            })

        return Response(data, status=200)


# ================================
# 5️⃣ Admin – Delete User
# ================================
class AdminDeleteUser(APIView):
    permission_classes = [IsRealAdmin]

    def delete(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return Response({"message": "User deleted."}, status=200)

        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=404)


# ================================
# 6️⃣ Admin – Update Role
# ================================
class AdminUpdateRole(APIView):
    permission_classes = [IsRealAdmin]

    def put(self, request, user_id):
        new_role = request.data.get("role")

        if new_role not in ["PATIENT", "DOCTOR", "ADMIN"]:
            return Response({"error": "Invalid role."}, status=400)

        try:
            profile = UserProfile.objects.get(user_id=user_id)

        except UserProfile.DoesNotExist:
            return Response({"error": "User profile not found."}, status=404)

        profile.user_type = new_role
        profile.save()

        return Response({
            "message": "Role updated.",
            "new_role": new_role
        }, status=200)
