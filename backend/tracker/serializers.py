from rest_framework import serializers
from .models import PlantedTree, TreeCareLog


class TreeCareLogSerializer(serializers.ModelSerializer):
    planted_tree = serializers.PrimaryKeyRelatedField(
        queryset=PlantedTree.objects.all(),
        required=False,
    )

    class Meta:
        model = TreeCareLog
        fields = '__all__'

    def validate_planted_tree(self, value):
        request = self.context['request']
        if value.calculation.user_id != request.user.id:
            raise serializers.ValidationError('Посадка не найдена в вашем аккаунте.')
        return value


class PlantedTreeSerializer(serializers.ModelSerializer):
    care_logs = TreeCareLogSerializer(many=True, read_only=True)

    class Meta:
        model = PlantedTree
        fields = '__all__'

    def validate(self, attrs):
        request = self.context['request']
        calculation = attrs.get('calculation', getattr(self.instance, 'calculation', None))
        pet = attrs.get('pet', getattr(self.instance, 'pet', None))
        eco_zone = attrs.get('eco_zone', getattr(self.instance, 'eco_zone', None))

        if calculation and calculation.user_id != request.user.id:
            raise serializers.ValidationError({
                'calculation': 'Расчёт не найден в вашем аккаунте.',
            })
        if pet and pet.user_id != request.user.id:
            raise serializers.ValidationError({
                'pet': 'Питомец не найден в вашем аккаунте.',
            })
        if calculation and calculation.pet_id and pet and calculation.pet_id != pet.id:
            raise serializers.ValidationError({
                'pet': 'Питомец должен совпадать с питомцем в выбранном расчёте.',
            })
        if eco_zone and not eco_zone.is_active:
            raise serializers.ValidationError({
                'eco_zone': 'Нельзя выбрать неактивную эко-зону.',
            })

        return attrs