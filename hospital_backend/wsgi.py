"""
WSGI config for hospital_backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

# استيراد مكتبة تفعيل ملفات الـ .env
try:
    from dotenv import load_dotenv
    # تحديد مسار ملف الـ .env (في نفس مستوى ملف manage.py)
    project_folder = os.path.expanduser('/home/youseff11/hospital_backend') # تأكد من اسم اليوزر والمجلد على السيرفر
    load_dotenv(os.path.join(project_folder, '.env'))
except ImportError:
    pass

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_backend.settings')

application = get_wsgi_application()