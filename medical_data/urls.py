# medical_data/urls.py (الكود الصحيح)

from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    SpecializationViewSet, 
    DiseaseViewSet, 
    DoctorListView, 
    AppointmentViewSet, 
    DoctorsByDiseaseView # <== تم إضافته هنا
) 

router = DefaultRouter()

# مسارات الـ ViewSet
router.register(r'specializations', SpecializationViewSet, basename='specialization')
router.register(r'diseases', DiseaseViewSet, basename='disease')
router.register(r'appointments', AppointmentViewSet, basename='appointment')

# مسارات الـ APIView/ListAPIView
urlpatterns = [
    *router.urls,
    
    path('doctors/', DoctorListView.as_view(), name='doctor-list'),
    
    # المسار الآن معرف بشكل صحيح
    path('doctors/by_disease/<int:disease_id>/', DoctorsByDiseaseView.as_view(), name='doctors-by-disease'),
]