from django import forms
from django.contrib import admin
from .models import (
    UserProfile, 
    DoctorProfile, 
    PatientProfile, 
    Specialization, 
    Disease, 
    Appointment,
    Prescription,
    PrescriptionMedicine,
    Medicine # <--- تم الإضافة هنا
)

# ========================================================
# 🔹 Custom Form for User Profiles Management
# ========================================================
class UserProfileAdminForm(forms.ModelForm):
    specialization = forms.ModelChoiceField(
        queryset=Specialization.objects.all(),
        required=False,
        label='Specialization (التخصص)',
        help_text='مطلوب فقط عند تحويل المستخدم إلى طبيب. سيتم إزالته من قائمة المرضى تلقائياً.'
    )

    class Meta:
        model = UserProfile
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.user_type == 'DOCTOR':
            doctor_profile = getattr(self.instance, 'doctorprofile', None)
            if doctor_profile:
                self.fields['specialization'].initial = doctor_profile.specialization

    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        specialization = cleaned_data.get('specialization')

        if user_type == 'DOCTOR' and not specialization:
            self.add_error('specialization', 'يجب اختيار التخصص عند تعيين المستخدم كطبيب!')

        return cleaned_data

    def save(self, commit=True):
        user_profile = super().save(commit=False)
        if commit:
            user_profile.save()

        user_type = self.cleaned_data.get('user_type')
        specialization = self.cleaned_data.get('specialization')

        if user_type == 'DOCTOR':
            patient_profile = getattr(user_profile, 'patientprofile', None)
            if patient_profile:
                patient_profile.delete()
            
            doctor_profile, created = DoctorProfile.objects.get_or_create(user_profile=user_profile)
            doctor_profile.specialization = specialization
            doctor_profile.save()

        elif user_type == 'PATIENT':
            doctor_profile = getattr(user_profile, 'doctorprofile', None)
            if doctor_profile:
                doctor_profile.delete()
            
            PatientProfile.objects.get_or_create(user_profile=user_profile)

        return user_profile

# ========================================================
# 1. User Profile Management
# ========================================================
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    form = UserProfileAdminForm 
    list_display = ('user', 'user_type', 'phone_number')
    list_filter = ('user_type',)
    search_fields = ('user__username', 'phone_number')
    raw_id_fields = ('user',)
    
    fieldsets = (
        ('User Details', {
            'fields': ('user', 'phone_number')
        }),
        ('Role & Specialization', {
            'fields': ('user_type', 'specialization'),
        }),
    )

# ========================================================
# 2. Medical Specializations
# ========================================================
@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'name_ar', 'icon')
    search_fields = ('name_en', 'name_ar')

# ========================================================
# 3. Doctor Profiles
# ========================================================
@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'specialization', 'rating')
    list_filter = ('specialization', 'rating')
    search_fields = ('user_profile__user__username',)

    def get_username(self, obj):
        return obj.user_profile.user.username
    get_username.short_description = 'Doctor Name'

# ========================================================
# 4. Patient Profiles
# ========================================================
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

# ========================================================
# 5. Diseases Management
# ========================================================
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

class PrescriptionInline(admin.StackedInline):
    model = Prescription
    extra = 0  
    show_change_link = True 

# ========================================================
# 6. Appointments Management
# ========================================================
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('get_patient_name', 'get_doctor_name', 'appointment_date', 'status')
    inlines = [PrescriptionInline]
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

# ========================================================
# 7. Medicine Inline (Linked to Prescription)
# ========================================================
class MedicineInline(admin.TabularInline):
    model = PrescriptionMedicine
    fields = ('medicine_name', 'dosage', 'duration', 'instructions')
    extra = 1 

# ========================================================
# 8. Prescription Management
# ========================================================
@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_patient', 'get_doctor', 'appointment_id', 'created_at')
    list_filter = ('created_at',) 
    inlines = [MedicineInline]
    
    raw_id_fields = ('appointment',) 
    
    search_fields = (
        'appointment__patient__user_profile__user__username',
        'appointment__doctor__user_profile__user__username',
        'diagnosis'
    )
    readonly_fields = ('created_at', 'updated_at')

    def get_patient(self, obj):
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

# ========================================================
# 9. Pharmacy / Medicine Management
# ========================================================
@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'name_ar', 'price')
    search_fields = ('name_en', 'name_ar', 'description')
    list_filter = ('price',)