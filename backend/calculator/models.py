from django.db import models
from django.conf import settings

class Pet(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pets', null=True, blank=True)
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=50)  # Собика, Кошка, Грызун и т.д.
    breed = models.CharField(max_length=100, blank=True)  # Порода (например, Шельти)
    weight_kg = models.FloatField()
    age_years = models.IntegerField(null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    death_date = models.DateField(null=True, blank=True)
    photo = models.ImageField(upload_to='pets/', null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.species})"

    @property
    def age_at_death_years(self):
        if not self.birth_date or not self.death_date:
            return None

        age = self.death_date.year - self.birth_date.year
        if (self.death_date.month, self.death_date.day) < (self.birth_date.month, self.birth_date.day):
            age -= 1
        return age


class TreeSpecies(models.Model):
    title = models.CharField(max_length=100)  # Вишня обыкновенная, Сосна и т.д.
    growth_rate = models.CharField(max_length=50)  # Средняя, Быстрая
    care_level = models.CharField(max_length=50)  # Минимальный, Высокий
    lifespan = models.CharField(max_length=100)  # Зависит от сорта, до 100 лет
    recommended_climate = models.CharField(max_length=100)
    recommended_soil = models.CharField(max_length=100)
    image = models.ImageField(upload_to='trees/', null=True, blank=True)

    def __str__(self):
        return self.title

class CapsuleCalculation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, null=True, blank=True)
    
    # Входные параметры из формы калькулятора (Макет 2)
    memorial_scenario = models.CharField(max_length=100)  # Семейный участок, Дерево на участке
    region = models.CharField(max_length=100)  # Средняя полоса России
    climate = models.CharField(max_length=100)  # Умеренный
    soil_type = models.CharField(max_length=100)  # Суглинок
    lighting = models.CharField(max_length=100)  # Частичная тень
    water_proximity = models.CharField(max_length=100)  # Требует уточнения
    care_level_pref = models.CharField(max_length=100)  # Минимальный
    desired_growth_time = models.CharField(max_length=100)  # Средний
    comment = models.TextField(blank=True)
    weight_kg = models.FloatField(null=True, blank=True)

    # Результаты расчета
    recommended_capsule_material = models.CharField(max_length=100, default="Мицелий / Прессованная целлюлоза")
    recommended_capsule_size = models.CharField(max_length=50, default="M (До 20 кг)")
    est_degradation_time = models.CharField(max_length=50, default="6-8 месяцев")
    estimated_degradation_months = models.FloatField(null=True, blank=True)
    recommended_tree = models.ForeignKey(TreeSpecies, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Расчет #{self.id} для {self.pet.name if self.pet else 'Демо'}"