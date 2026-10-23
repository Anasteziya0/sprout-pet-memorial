from rest_framework import serializers
from .degradation import CLIMATE_FACTORS, SOIL_FACTORS, degradation_breakdown
from .models import CapsuleCalculation, Pet, TreeSpecies

class TreeSpeciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreeSpecies
        fields = [
            'id',
            'title',
            'growth_rate',
            'care_level',
            'lifespan',
            'recommended_climate',
            'recommended_soil',
            'image',
        ]


class PetSerializer(serializers.ModelSerializer):
    age_years = serializers.IntegerField(source='age_at_death_years', read_only=True, allow_null=True)

    def to_internal_value(self, data):
        normalized_data = {field: data.get(field) for field in data}
        for field in ('birth_date', 'death_date'):
            if normalized_data.get(field) == '':
                normalized_data[field] = None
        return super().to_internal_value(normalized_data)

    def validate(self, attrs):
        birth_date = attrs.get('birth_date', getattr(self.instance, 'birth_date', None))
        death_date = attrs.get('death_date', getattr(self.instance, 'death_date', None))
        if birth_date and death_date and death_date < birth_date:
            raise serializers.ValidationError({
                'death_date': 'Дата ухода не может быть раньше даты рождения.',
            })
        return attrs

    def validate_photo(self, value):
        if value and value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError('Размер фотографии не должен превышать 10 МБ.')
        return value

    class Meta:
        model = Pet
        fields = [
            'id',
            'name',
            'species',
            'breed',
            'weight_kg',
            'age_years',
            'birth_date',
            'death_date',
            'photo',
        ]


class CalculationRequestSerializer(serializers.Serializer):
    weight = serializers.FloatField(required=False, default=10, min_value=0.1)
    scenario = serializers.CharField(max_length=100)
    region = serializers.CharField(max_length=100)
    climate = serializers.CharField(max_length=100)
    soil = serializers.CharField(max_length=100)
    lighting = serializers.CharField(max_length=100)
    water_proximity = serializers.CharField(max_length=100, required=False, allow_blank=True, default='')
    care_level_pref = serializers.CharField(max_length=100, required=False, allow_blank=True, default='')
    desired_growth_time = serializers.CharField(max_length=100, required=False, allow_blank=True, default='')
    comment = serializers.CharField(required=False, allow_blank=True, default='')
    pet_id = serializers.IntegerField(required=False, allow_null=True)

    def validate_climate(self, value):
        if value.strip().casefold() not in CLIMATE_FACTORS:
            raise serializers.ValidationError('Выберите поддерживаемый климатический тип.')
        return value

    def validate_soil(self, value):
        if value.strip().casefold() not in SOIL_FACTORS:
            raise serializers.ValidationError('Выберите поддерживаемый тип почвы.')
        return value

    def validate_pet_id(self, value):
        request = self.context['request']
        if value is not None and not request.user.is_authenticated:
            raise serializers.ValidationError('Для привязки питомца необходимо войти в аккаунт.')
        if value is not None and not Pet.objects.filter(pk=value, user=request.user).exists():
            raise serializers.ValidationError('Питомец не найден в вашем аккаунте.')
        return value

class CalculationSerializer(serializers.ModelSerializer):
    recommended_tree = TreeSpeciesSerializer(read_only=True)
    degradation_breakdown = serializers.SerializerMethodField()

    def get_degradation_breakdown(self, calculation):
        weight = calculation.weight_kg
        if weight is None and calculation.pet_id:
            weight = calculation.pet.weight_kg
        if weight is None:
            return None
        return degradation_breakdown(weight, calculation.soil_type, calculation.climate)

    class Meta:
        model = CapsuleCalculation
        fields = '__all__'