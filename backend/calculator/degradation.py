BASE_DEGRADATION_MONTHS = 6.0

WEIGHT_FACTORS = (
    (5.0, 0.9),
    (20.0, 1.0),
)
OVER_20_KG_FACTOR = 1.2

SOIL_FACTORS = {
    'чернозем': 0.9,
    'чернозём': 0.9,
    'черноземная': 0.9,
    'чернозёмная': 0.9,
    'black soil': 0.9,
    'песок': 1.0,
    'песчаная': 1.0,
    'sand': 1.0,
    'sandy': 1.0,
    'суглинок': 1.0,
    'loam': 1.0,
    'глина': 1.3,
    'глинистая': 1.3,
    'clay': 1.3,
}

CLIMATE_FACTORS = {
    'южный': 0.9,
    'south': 0.9,
    'southern': 0.9,
    'умеренный': 1.0,
    'temperate': 1.0,
    'континентальный': 1.1,
    'continental': 1.1,
    'северный': 1.3,
    'north': 1.3,
    'northern': 1.3,
}


def weight_factor(weight):
    if weight <= 0:
        raise ValueError('Вес питомца должен быть больше нуля.')
    for maximum, factor in WEIGHT_FACTORS:
        if weight < maximum:
            return factor
    if weight <= WEIGHT_FACTORS[-1][0]:
        return WEIGHT_FACTORS[-1][1]
    return OVER_20_KG_FACTOR


def soil_factor(soil):
    return SOIL_FACTORS[soil.strip().casefold()]


def climate_factor(climate):
    return CLIMATE_FACTORS[climate.strip().casefold()]


def degradation_breakdown(weight, soil, climate):
    k_weight = weight_factor(weight)
    k_soil = soil_factor(soil)
    k_climate = climate_factor(climate)
    total_months = round(BASE_DEGRADATION_MONTHS * k_weight * k_soil * k_climate, 1)
    return {
        'base_months': BASE_DEGRADATION_MONTHS,
        'weight_kg': weight,
        'k_weight': k_weight,
        'k_soil': k_soil,
        'k_climate': k_climate,
        'total_months': total_months,
    }
