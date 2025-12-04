
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')), # تغيير المسار لتنظيم الـ API
    # 🌟 إضافة مسارات medical_data
    path('api/', include('medical_data.urls')), 
]