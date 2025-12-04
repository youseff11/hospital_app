# users/signals.py

from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserProfile, PatientProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    هذه الدالة تستمع لحدث حفظ (Save) نموذج المستخدم (User).
    إذا كان المستخدم قد تم إنشاؤه للتو (created=True)، تقوم بإنشاء 
    UserProfile و PatientProfile مرتبطين به تلقائياً.
    """
    if created:
        # 1. إنشاء ملف التعريف الأساسي (UserProfile)
        # يتم تعيين user_type افتراضياً على 'PATIENT'
        user_profile = UserProfile.objects.create(user=instance)
        
        # 2. إنشاء ملف المريض (PatientProfile) المرتبط بملف التعريف الأساسي
        PatientProfile.objects.create(user_profile=user_profile)