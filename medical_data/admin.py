from django.contrib import admin
from .models import Specialization, Disease, Appointment
from users.models import DoctorProfile, PatientProfile


# 1. Specialization Admin
@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'description_en', 'icon')
    search_fields = ('name_en',)


# 2. Disease Admin
@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'specialization')
    list_filter = ('specialization',)
    search_fields = ('name_en', 'symptoms')


# 3. Appointment Admin
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'appointment_date', 'status')
    list_filter = ('status', 'appointment_date')
    search_fields = (
        'patient__user_profile__user__username',
        'doctor__user_profile__user__username'
    )


# 4. DoctorProfile Admin
@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'specialization', 'rating')
    list_filter = ('specialization', 'rating')
    search_fields = ('user_profile__user__username',)


# 5. PatientProfile Admin
@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('user_profile',)
    search_fields = ('user_profile__user__username',)
