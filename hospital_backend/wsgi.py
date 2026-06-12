"""
WSGI config for hospital_backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

# محاولة تحميل متغيرات البيئة من ملف .env بشكل آمن
try:
    from dotenv import load_dotenv
    # تأكد أن هذا هو المسار الصحيح لمجلد الـ backend اللي جواه ملف .env
    project_folder = '/home/youseff11/hospital_backend' 
    load_dotenv(os.path.join(project_folder, '.env'))
except Exception as e:
    print(f"Dotenv loading failed: {e}")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_backend.settings')

application = get_wsgi_application()