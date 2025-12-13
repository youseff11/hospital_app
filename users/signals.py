# users/signals.py

# from django.db.models.signals import post_save
# from django.contrib.auth.models import User
# from django.dispatch import receiver
# from .models import UserProfile, PatientProfile

# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):

#     if created:
#         user_profile = UserProfile.objects.create(user=instance)
        
#         PatientProfile.objects.create(user_profile=user_profile)