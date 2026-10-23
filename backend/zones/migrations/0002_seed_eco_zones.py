from django.db import migrations


ZONES = [
    {
        'name': 'Эко-парк «Северный»',
        'zone_type': 'Мемориальный лес',
        'address': 'г. Санкт-Петербург, пос. Левашово',
        'latitude': 60.0825,
        'longitude': 30.2512,
        'has_care_service': True,
        'rules': 'Посадка саженцев согласовывается с лесничим. Разрешены биоразлагаемые капсулы.',
        'is_active': True,
    },
    {
        'name': 'Зелёный мемориальный парк',
        'zone_type': 'Лесопарк',
        'address': 'г. Москва, ул. Поляны, 4с1',
        'latitude': 55.5674,
        'longitude': 37.5489,
        'has_care_service': True,
        'rules': 'Уход за саженцами осуществляется штатной службой парка первые 2 года.',
        'is_active': True,
    },
    {
        'name': 'Лес памяти «Исток»',
        'zone_type': 'Заповедная зона',
        'address': 'Московская область, г.о. Истра',
        'latitude': 55.9116,
        'longitude': 36.8643,
        'has_care_service': True,
        'rules': 'Вход свободный. Посещение по предварительной записи через приложение.',
        'is_active': True,
    },
    {
        'name': 'Эко-парк «Южный»',
        'zone_type': 'Сад памяти',
        'address': 'г. Краснодар, ул. Ставропольская',
        'latitude': 45.0211,
        'longitude': 38.9972,
        'has_care_service': False,
        'rules': 'Самостоятельный уход за зелеными насаждениями.',
        'is_active': True,
    },
]


def seed_eco_zones(apps, schema_editor):
    EcoZone = apps.get_model('zones', 'EcoZone')
    database = schema_editor.connection.alias

    for zone in ZONES:
        EcoZone.objects.using(database).get_or_create(
            name=zone['name'],
            address=zone['address'],
            defaults=zone,
        )


def remove_eco_zones(apps, schema_editor):
    EcoZone = apps.get_model('zones', 'EcoZone')
    database = schema_editor.connection.alias

    for zone in ZONES:
        EcoZone.objects.using(database).filter(
            name=zone['name'],
            address=zone['address'],
        ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('zones', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_eco_zones, remove_eco_zones),
    ]
