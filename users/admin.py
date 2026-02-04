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
    list_display = ('name_en', 'name_ar', 'icon') # عرض الاسم بالعربي والإنجليزي
    search_fields = ('name_en', 'name_ar')


# 3. إدارة بروفايل الأطباء
@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'specialization', 'rating')
    list_filter = ('specialization', 'rating')
    search_fields = ('user_profile__user__username',)

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


# 5. إدارة الأمراض (تم تحديث العرض هنا)
@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    # عرض الاسم العربي والإنجليزي والتخصص في القائمة الرئيسية
    list_display = ('name_en', 'name_ar', 'specialization') 
    list_filter = ('specialization',)
    search_fields = ('name_en', 'name_ar', 'symptoms_en', 'symptoms_ar')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name_en', 'name_ar', 'specialization')
        }),
        ('Symptoms & Description', {
            'fields': ('symptoms_en', 'symptoms_ar', 'symptoms'),
            'description': 'Enter descriptions for both languages.'
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
    
# 7. إدارة الأدوية كجزء مدمج (Inline)
class MedicineInline(admin.TabularInline):
    model = PrescriptionMedicine
    extra = 1  # يظهر حقل واحد فارغ افتراضياً لإضافة دواء جديد

# 8. إدارة الروشتات
@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    # list_display تساعدك في رؤية المريض والتاريخ من القائمة الرئيسية للروشتات
    list_display = ('get_patient', 'get_doctor', 'created_at')
    inlines = [MedicineInline]
    search_fields = ('appointment__patient__user_profile__user__username',)

    # دالة لجلب اسم المريض في القائمة
    def get_patient(self, obj):
        return obj.appointment.patient.user_profile.user.username
    get_patient.short_description = 'Patient Name'

    # دالة لجلب اسم الطبيب في القائمة
    def get_doctor(self, obj):
        return obj.appointment.doctor.user_profile.user.username
    get_doctor.short_description = 'Doctor Name'