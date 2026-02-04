from django.contrib import admin
from .models import (
    UserProfile, 
    DoctorProfile, 
    PatientProfile, 
    Specialization, 
    Disease, 
    Appointment,
    Prescription,
    PrescriptionMedicine
)

# 1. User Profile Management
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type', 'phone_number')
    list_filter = ('user_type',)
    search_fields = ('user__username', 'phone_number')
    raw_id_fields = ('user',)


# 2. Medical Specializations
@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'name_ar', 'icon')
    search_fields = ('name_en', 'name_ar')


# 3. Doctor Profiles
@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'specialization', 'rating')
    list_filter = ('specialization', 'rating')
    search_fields = ('user_profile__user__username',)

    def get_username(self, obj):
        return obj.user_profile.user.username
    get_username.short_description = 'Doctor Name'


# 4. Patient Profiles
@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'phone')
    search_fields = ('user_profile__user__username',)

    def get_username(self, obj):
        return obj.user_profile.user.username
    get_username.short_description = 'Patient Name'

    def phone(self, obj):
        return obj.user_profile.phone_number
    phone.short_description = 'Phone Number'


# 5. Diseases Management
@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'name_ar', 'specialization') 
    list_filter = ('specialization',)
    search_fields = ('name_en', 'name_ar', 'symptoms_en', 'symptoms_ar')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name_en', 'name_ar', 'specialization')
        }),
        ('Symptoms & Description', {
            'fields': ('symptoms_en', 'symptoms_ar'),
        }),
    )


# 6. Appointments Management
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('get_patient_name', 'get_doctor_name', 'appointment_date', 'status')
    list_filter = ('status', 'appointment_date')
    search_fields = (
        'patient__user_profile__user__username',
        'doctor__user_profile__user__username'
    )
    ordering = ('-appointment_date',)

    def get_patient_name(self, obj):
        return obj.patient.user_profile.user.username
    get_patient_name.short_description = 'Patient'

    def get_doctor_name(self, obj):
        return obj.doctor.user_profile.user.username
    get_doctor_name.short_description = 'Doctor'


# 7. Medicine Inline (Linked to Prescription)
class MedicineInline(admin.TabularInline):
    model = PrescriptionMedicine
    # تم التعديل لاستخدام حقل instructions الجديد
    fields = ('medicine_name', 'dosage', 'duration', 'instructions')
    extra = 1 


# 8. Prescription Management
@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('get_patient', 'get_doctor', 'created_at')
    inlines = [MedicineInline]
    search_fields = ('appointment__patient__user_profile__user__username',)
    readonly_fields = ('created_at', 'updated_at')

    def get_patient(self, obj):
        # تم تعديل طريقة الوصول هنا لتجنب الـ AttributeError
        try:
            return obj.appointment.patient.user_profile.user.username
        except:
            return "N/A"
    get_patient.short_description = 'Patient'

    def get_doctor(self, obj):
        try:
            return obj.appointment.doctor.user_profile.user.username
        except:
            return "N/A"
    get_doctor.short_description = 'Doctor'

    fieldsets = (
        ('Appointment Details', {
            'fields': ('appointment',)
        }),
        ('Medical Diagnosis', {
            'fields': ('diagnosis',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',) 
        }),
    )