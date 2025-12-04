from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import Specialization
from .serializers import SpecializationSerializer

class SpecializationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List of medical specializations (read-only)
    /api/specializations/
    """
    queryset = Specialization.objects.all()
    serializer_class = SpecializationSerializer
    permission_classes = [AllowAny]