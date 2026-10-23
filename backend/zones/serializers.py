from rest_framework import serializers
from .models import EcoZone

class EcoZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = EcoZone
        fields = ['id', 'name', 'zone_type', 'address', 'latitude', 'longitude', 'has_care_service', 'rules']


class EcoZoneAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = EcoZone
        fields = '__all__'