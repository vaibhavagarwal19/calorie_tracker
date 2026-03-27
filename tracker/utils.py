def calculate_bmr(sex, weight_kg, height_cm, age):
    if sex == 'male':
        return round(66.4730 + (13.7516 * weight_kg) + (5.0033 * height_cm) - (6.7550 * age), 3)
    return round(655.0955 + (9.5634 * weight_kg) + (1.8496 * height_cm) - (4.6756 * age), 3)


def calculate_activity_calories(met_value, weight_kg, duration_minutes):
    return round(met_value * weight_kg * (duration_minutes / 60), 2)
