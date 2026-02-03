# users/admin.py

from django.contrib import admin
from .models import (
    UserProfile, 
    DoctorProfile, 
    PatientProfile, 
    Specialization, 
    Disease, 
    Appointment
)

# 1. إدارة ملف تعريف المستخدم الأساسي
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type', 'phone_number')
    list_filter = ('user_type',)
    search_fields = ('user__username', 'phone_number')
    raw_id_fields = ('user',)


# 2. إدارة التخصصات الطبية
@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'name_ar', 'icon')
    search_fields = ('name_en', 'name_ar')


# 3. إدارة بروفايل الأطباء
@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'specialization', 'rating')
    list_filter = ('specialization', 'rating')
    search_fields = ('user_profile__user__username',)

    # دالة لجلب اسم المستخدم مباشرة في لوحة التحكم
    def get_username(self, obj):
        return obj.user_profile.user.username
    get_username.short_description = 'Doctor Name'


# 4. إدارة بروفايل المرضى
@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('get_username',)
    search_fields = ('user_profile__user__username',)

    def get_username(self, obj):
        return obj.user_profile.user.username
    get_username.short_description = 'Patient Name'


# 5. إدارة الأمراض
@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'specialization')
    list_filter = ('specialization',)
    search_fields = ('name_en', 'symptoms')


# 6. إدارة المواعيد
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'appointment_date', 'status')
    list_filter = ('status', 'appointment_date')
    search_fields = (
        'patient__user_profile__user__username',
        'doctor__user_profile__user__username'
    )