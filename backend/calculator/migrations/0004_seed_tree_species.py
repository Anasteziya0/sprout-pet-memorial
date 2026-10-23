from django.db import migrations


TREE_SPECIES = [
    {
        'title': 'Сосна обыкновенная',
        'growth_rate': 'Средний',
        'care_level': 'Минимальный',
        'lifespan': 'До 300 лет',
        'recommended_climate': 'Умеренный, Континентальный, Северный, Temperate, Continental, Northern',
        'recommended_soil': 'Песчаная, Суглинок, Sandy, Loam',
    },
    {
        'title': 'Берёза повислая',
        'growth_rate': 'Быстрый',
        'care_level': 'Минимальный',
        'lifespan': 'До 120 лет',
        'recommended_climate': 'Умеренный, Континентальный, Северный, Temperate, Continental, Northern',
        'recommended_soil': 'Песчаная, Суглинок, Глинистая, Sandy, Loam, Clay',
    },
    {
        'title': 'Ель европейская',
        'growth_rate': 'Медленный',
        'care_level': 'Средний',
        'lifespan': 'До 300 лет',
        'recommended_climate': 'Умеренный, Континентальный, Северный, Temperate, Continental, Northern',
        'recommended_soil': 'Суглинок, Глинистая, Loam, Clay',
    },
    {
        'title': 'Рябина обыкновенная',
        'growth_rate': 'Средний',
        'care_level': 'Минимальный',
        'lifespan': 'До 100 лет',
        'recommended_climate': 'Умеренный, Континентальный, Северный, Temperate, Continental, Northern',
        'recommended_soil': 'Чернозём, Суглинок, Глинистая, Black soil, Loam, Clay',
    },
    {
        'title': 'Лиственница сибирская',
        'growth_rate': 'Быстрый',
        'care_level': 'Минимальный',
        'lifespan': 'До 400 лет',
        'recommended_climate': 'Континентальный, Северный, Continental, Northern',
        'recommended_soil': 'Песчаная, Суглинок, Sandy, Loam',
    },
    {
        'title': 'Клён остролистный',
        'growth_rate': 'Средний',
        'care_level': 'Средний',
        'lifespan': 'До 200 лет',
        'recommended_climate': 'Умеренный, Континентальный, Temperate, Continental',
        'recommended_soil': 'Чернозём, Суглинок, Black soil, Loam',
    },
    {
        'title': 'Липа мелколистная',
        'growth_rate': 'Медленный',
        'care_level': 'Средний',
        'lifespan': 'До 500 лет',
        'recommended_climate': 'Умеренный, Континентальный, Южный, Temperate, Continental, Southern',
        'recommended_soil': 'Чернозём, Суглинок, Black soil, Loam',
    },
    {
        'title': 'Дуб черешчатый',
        'growth_rate': 'Медленный',
        'care_level': 'Средний',
        'lifespan': 'До 500 лет',
        'recommended_climate': 'Умеренный, Континентальный, Южный, Temperate, Continental, Southern',
        'recommended_soil': 'Чернозём, Суглинок, Глинистая, Black soil, Loam, Clay',
    },
    {
        'title': 'Каштан посевной',
        'growth_rate': 'Средний',
        'care_level': 'Средний',
        'lifespan': 'До 300 лет',
        'recommended_climate': 'Южный, Умеренный, Southern, Temperate',
        'recommended_soil': 'Чернозём, Суглинок, Black soil, Loam',
    },
    {
        'title': 'Граб обыкновенный',
        'growth_rate': 'Медленный',
        'care_level': 'Средний',
        'lifespan': 'До 150 лет',
        'recommended_climate': 'Южный, Умеренный, Southern, Temperate',
        'recommended_soil': 'Чернозём, Суглинок, Глинистая, Black soil, Loam, Clay',
    },
]


def seed_tree_species(apps, schema_editor):
    TreeSpecies = apps.get_model('calculator', 'TreeSpecies')
    database = schema_editor.connection.alias
    manager = TreeSpecies.objects.using(database)

    if manager.exists():
        return

    manager.bulk_create([TreeSpecies(**species) for species in TREE_SPECIES])


def remove_seeded_tree_species(apps, schema_editor):
    TreeSpecies = apps.get_model('calculator', 'TreeSpecies')
    database = schema_editor.connection.alias

    for species in TREE_SPECIES:
        TreeSpecies.objects.using(database).filter(**species).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('calculator', '0003_capsulecalculation_estimated_degradation_months_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_tree_species, remove_seeded_tree_species),
    ]
