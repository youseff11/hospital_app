# medical_data/admin.py

from django.contrib import admin
from .models import Specialization, Disease, Appointment
from users.models import DoctorProfile, PatientProfile 

# 1. تسجيل نموذج التخصص
@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ('name_ar', 'description_ar')
    search_fields = ('name_ar',)

# 2. تسجيل نموذج المرض
@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display = ('name_ar', 'specialization')
    list_filter = ('specialization',)
    search_fields = ('name_ar', 'symptoms')

# 3. تسجيل نموذج الموعد
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'appointment_date', 'status')
    list_filter = ('status', 'appointment_date')
    # ❌ تم إزالة raw_id_fields هنا
    # raw_id_fields = ('patient', 'doctor') 

# 4. تسجيل نماذج المستخدمين ذات الصلة (تصحيح الأخطاء E108 و E003)

@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'specialization', 'rating')
    list_filter = ('specialization', 'rating')
    search_fields = ('user_profile__user__username',)
    # ❌ تم إزالة raw_id_fields هنا
    # raw_id_fields = ('user_profile', 'specialization') 

@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('user_profile',) 
    search_fields = ('user_profile__user__username',)
    # ❌ تم إزالة raw_id_fields هنا
    # raw_id_fields = ('user_profile',)