from rest_framework.routers import DefaultRouter
from .views import SpecializationViewSet

router = DefaultRouter()
# إنشاء مسار /api/specializations/
router.register(r'specializations', SpecializationViewSet)

urlpatterns = router.urls