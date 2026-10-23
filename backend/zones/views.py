from rest_framework import generics, permissions
from .models import EcoZone
from .serializers import EcoZoneAdminSerializer, EcoZoneSerializer

class EcoZoneListView(generics.ListAPIView):
    """Эндпоинт для получения списка эко-зон (отображение маркеров на ГИС-карте)"""
    queryset = EcoZone.objects.filter(is_active=True)
    serializer_class = EcoZoneSerializer


class EcoZoneAdminListCreateView(generics.ListCreateAPIView):
    serializer_class = EcoZoneAdminSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return EcoZone.objects.all().order_by('id')


class EcoZoneAdminDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = EcoZone.objects.all()
    serializer_class = EcoZoneAdminSerializer
    permission_classes = [permissions.IsAdminUser]