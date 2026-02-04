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

    def get_username(self, obj):
        return obj.user_profile.user.username
    get_username.short_description = 'اسم الطبيب'


# 4. إدارة بروفايل المرضى
@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'phone')
    search_fields = ('user_profile__user__username',)

    def get_username(self, obj):
        return obj.user_profile.user.username
    get_username.short_description = 'اسم المريض'

    def phone(self, obj):
        return obj.user_profile.phone_number
    phone.short_description = 'رقم الهاتف'


# 5. إدارة الأمراض
@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display = ('name_ar', 'name_en', 'specialization') 
    list_filter = ('specialization',)
    search_fields = ('name_en', 'name_ar', 'symptoms_en', 'symptoms_ar')
    
    fieldsets = (
        ('المعلومات الأساسية (Basic Info)', {
            'fields': ('name_en', 'name_ar', 'specialization')
        }),
        ('التوصيف والأعراض (Symptoms)', {
            'fields': ('symptoms_en', 'symptoms_ar'),
        }),
    )


# 6. إدارة المواعيد
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'appointment_date', 'status')
    list_filter = ('status', 'appointment_date')
    search_fields = (
        'patient__user_profile__user__username',
        'doctor__user_profile__user__username'
    )
    # ترتيب المواعيد من الأحدث للأقدم
    ordering = ('-appointment_date',)


# 7. إدارة الأدوية كجزء مدمج (Tabular Inline)
class MedicineInline(admin.TabularInline):
    model = PrescriptionMedicine
    # عرض الحقول الجديدة بعد الدمج
    fields = ('medicine_name', 'dosage', 'duration', 'instructions')
    extra = 1  # يظهر حقل فارغ واحد للإضافة السريعة


# 8. إدارة الروشتات
@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('get_patient', 'get_doctor', 'created_at')
    # إضافة الأدوية داخل صفحة الروشتة
    inlines = [MedicineInline]
    search_fields = ('appointment__patient__user_profile__user__username',)
    readonly_fields = ('created_at', 'updated_at')

    def get_patient(self, obj):
        return obj.appointment.patient.user_profile.user.username
    get_patient.short_description = 'المريض'

    def get_doctor(self, obj):
        return obj.appointment.doctor.user_profile.user.username
    get_doctor.short_description = 'الطبيب'

    fieldsets = (
        ('بيانات الموعد', {
            'fields': ('appointment',)
        }),
        ('التشخيص الطبي', {
            'fields': ('diagnosis',)
        }),
        ('التوقيت', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',) # إخفاء التوقيتات خلف قائمة منسدلة
        }),
    )

# 9. تسجيل الأدوية بشكل منفصل (اختياري)
@admin.register(PrescriptionMedicine)
class PrescriptionMedicineAdmin(admin.ModelAdmin):
    list_display = ('medicine_name', 'prescription', 'dosage')
    search_fields = ('medicine_name',)