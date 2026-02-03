from django.db import models
from django.contrib.auth.models import User

# 1. التخصصات الطبية
class Specialization(models.Model):
    name_en = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Specialization Name (EN)",
    )
    name_ar = models.CharField(  # أضفنا هذا الحقل لحل مشكلة الـ Admin
        max_length=100,
        unique=True,
        verbose_name="اسم التخصص (بالعربي)",
        null=True,
        blank=True
    )
    description_en = models.TextField(
        verbose_name="Description",
        blank=True,
        null=True
    )
    icon = models.CharField(
        max_length=50,
        verbose_name="Icon Class",
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name_en

    class Meta:
        verbose_name = "Medical Specialization"
        verbose_name_plural = "Medical Specializations"


# 2. ملف تعريف المستخدم الأساسي
class UserProfile(models.Model):
    USER_TYPE_CHOICES = (
        ('PATIENT', 'PATIENT'),
        ('DOCTOR', 'DOCTOR'),
        ('ADMIN', 'ADMIN'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default='PATIENT',
    )
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_user_type_display()}"


# 3. بروفايل المريض
class PatientProfile(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, primary_key=True)
    date_of_birth = models.DateField(null=True, blank=True)
    medical_history = models.TextField(blank=True)

    def __str__(self):
        return f"Patient Profile: {self.user_profile.user.username}"


# 4. بروفايل الطبيب
class DoctorProfile(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, primary_key=True)
    specialization = models.ForeignKey(
        Specialization, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name="Specialization"
    )
    license_number = models.CharField(max_length=50, unique=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    
    def __str__(self):
        spec_name = self.specialization.name_en if self.specialization else 'Undefined'
        return f"Doctor: {self.user_profile.user.username} ({spec_name})"
    
    class Meta:
        verbose_name = "Doctor Profile"
        verbose_name_plural = "Doctor Profiles"


# 5. الأمراض (تم التحديث هنا لإضافة الأعراض بالعربي والإنجليزي)
class Disease(models.Model):
    name_en = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="Disease Name (EN)"
    )
    name_ar = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="اسم المرض (بالعربي)",
        null=True,
        blank=True
    )
    specialization = models.ForeignKey(
        Specialization,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Related Specialization"
    )
    # الحقل القديم (للاحتياط)
    symptoms = models.TextField(
        verbose_name="Symptoms (General)",
        blank=True,
        null=True
    )
    # الحقول الجديدة للترجمة في Flutter
    symptoms_en = models.TextField(
        verbose_name="Symptoms (EN)",
        blank=True,
        null=True
    )
    symptoms_ar = models.TextField(
        verbose_name="الأعراض (بالعربي)",
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name_en

    class Meta:
        verbose_name = "Disease"
        verbose_name_plural = "Diseases"


# 6. المواعيد
class Appointment(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending Confirmation'),
        ('CONFIRMED', 'Confirmed'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    )

    patient = models.ForeignKey(
        PatientProfile,
        on_delete=models.CASCADE,
        verbose_name="Patient"
    )
    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.CASCADE,
        verbose_name="Doctor"
    )
    appointment_date = models.DateTimeField(
        verbose_name="Appointment Date and Time"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDING',
        verbose_name="Status"
    )
    notes = models.TextField(
        verbose_name="Notes",
        blank=True,
        null=True
    )

    def __str__(self):
        patient_name = self.patient.user_profile.user.username
        doctor_name = self.doctor.user_profile.user.username
        return f"Appointment {patient_name} with Dr. {doctor_name}"

    class Meta:
        verbose_name = "Appointment"
        verbose_name_plural = "Appointments"
        ordering = ['appointment_date']