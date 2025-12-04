from django.db import models
from django.contrib.auth.models import User 

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


class PatientProfile(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, primary_key=True)
    date_of_birth = models.DateField(null=True, blank=True)
    medical_history = models.TextField(blank=True)

    def __str__(self):
        return f"Patient Profile: {self.user_profile.user.username}"


class DoctorProfile(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, primary_key=True)
    
    specialization = models.ForeignKey(
        'medical_data.Specialization',
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name="Specialization"
    )
    
    license_number = models.CharField(max_length=50, unique=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    
    def __str__(self):
        spec_name = self.specialization.name if self.specialization else 'Undefined'
        return f"Doctor: {self.user_profile.user.username} ({spec_name})"
    
    class Meta:
        verbose_name = "Doctor Profile"
        verbose_name_plural = "Doctor Profiles"