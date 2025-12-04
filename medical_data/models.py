from django.db import models
from users.models import DoctorProfile, PatientProfile 

class Specialization(models.Model):
    name_ar = models.CharField(max_length=100, unique=True, verbose_name="Specialization Name (Arabic)")
    description_ar = models.TextField(verbose_name="Description (Arabic)", blank=True, null=True)
    icon = models.CharField(max_length=50, verbose_name="Icon Class", blank=True, null=True)

    def __str__(self):
        return self.name_ar
    
    class Meta:
        verbose_name = "Medical Specialization"
        verbose_name_plural = "Medical Specializations"

class Disease(models.Model):
    name_ar = models.CharField(max_length=150, unique=True, verbose_name="Disease Name (Arabic)")
    specialization = models.ForeignKey(Specialization, on_delete=models.SET_NULL, null=True, 
                                     verbose_name="Related Specialization")
    symptoms = models.TextField(verbose_name="Symptoms", blank=True, null=True)

    def __str__(self):
        return self.name_ar

    class Meta:
        verbose_name = "Disease"
        verbose_name_plural = "Diseases"

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending Confirmation'),
        ('CONFIRMED', 'Confirmed'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    )
    
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, verbose_name="Patient")
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, verbose_name="Doctor")
    appointment_date = models.DateTimeField(verbose_name="Appointment Date and Time")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING', verbose_name="Status")
    notes = models.TextField(verbose_name="Notes", blank=True, null=True)

    def __str__(self):
        return f"Appointment {self.patient.user_profile.user.username} with Dr. {self.doctor.user_profile.user.username}"

    class Meta:
        verbose_name = "Appointment"
        verbose_name_plural = "Appointments"
        ordering = ['appointment_date']