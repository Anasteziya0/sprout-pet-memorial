from django.db import models
from calculator.models import CapsuleCalculation, Pet, TreeSpecies
from zones.models import EcoZone

class PlantedTree(models.Model):
    calculation = models.OneToOneField(CapsuleCalculation, on_delete=models.CASCADE, related_name='planted_tree')
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE)
    tree_species = models.ForeignKey(TreeSpecies, on_delete=models.SET_NULL, null=True)
    eco_zone = models.ForeignKey(EcoZone, on_delete=models.SET_NULL, null=True, blank=True)
    
    planting_date = models.DateField()
    location_details = models.CharField(max_length=255)  # Аллея памяти — участок А-12
    initial_height_cm = models.FloatField(default=142.0)
    current_height_cm = models.FloatField(default=164.0)
    trunk_diameter_cm = models.FloatField(default=2.8)
    status = models.CharField(max_length=50, default="Растёт")

    def __str__(self):
        return f"Дерево для {self.pet.name}"

class TreeCareLog(models.Model):
    planted_tree = models.ForeignKey(PlantedTree, on_delete=models.CASCADE, related_name='care_logs')
    event_date = models.DateField()
    title = models.CharField(max_length=150)  # Осмотр и замер, Полив и мульчирование
    description = models.TextField(blank=True)
    photo = models.ImageField(upload_to='tree_logs/', null=True, blank=True)

    class Meta:
        ordering = ['-event_date']