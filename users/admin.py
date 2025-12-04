# users/admin.py

from django.contrib import admin
from .models import UserProfile # استيراد النموذج الأساسي

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type', 'phone_number')
    list_filter = ('user_type',)
    search_fields = ('user__username', 'phone_number')
    raw_id_fields = ('user',) # نستخدم هذا لتسهيل ربط المستخدم بملف التعريف