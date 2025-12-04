# users/apps.py

from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    
    # 🌟🌟🌟 إضافة هذه الدالة لربط ملف الإشارات 🌟🌟🌟
    def ready(self):
        # استيراد ملف الإشارات عند بدء تشغيل التطبيق
        import users.signals