"""Prototype household-water estimates. Constants vary by fixture and locality."""
SHOWER_FLOW_RATE = 9.0
TOILET_FLUSH_VOLUME = 6.0
BATH_VOLUME = 120.0
KITCHEN_TAP_DAILY = 18.0
DISHWASHER_LOAD = 12.0
LAUNDRY_LOAD = {'efficient': 50.0, 'standard': 90.0}
GARDENING_SESSION = 80.0
CAR_WASH = 120.0

def calculate(data):
    h = data['household_size']
    shower = h * data['showers_per_person'] * data['shower_minutes'] * SHOWER_FLOW_RATE
    toilet = h * data['flushes_per_person'] * TOILET_FLUSH_VOLUME
    baths = data['baths_per_week'] * BATH_VOLUME / 7
    kitchen = h * KITCHEN_TAP_DAILY + data['dishwasher_loads_per_week'] * DISHWASHER_LOAD / 7
    laundry = data['laundry_loads_per_week'] * LAUNDRY_LOAD[data['machine_type']] / 7
    outdoor = (data['garden_sessions_per_week'] * GARDENING_SESSION + data['car_washes_per_month'] * CAR_WASH / 4.345) / 7
    breakdown = {'Bathroom': round(shower + toilet + baths, 1), 'Kitchen': round(kitchen, 1), 'Laundry': round(laundry, 1), 'Outdoor': round(outdoor, 1), 'Other': 0}
    daily = round(sum(breakdown.values()), 1)
    return {'daily_total': daily, 'monthly_total': round(daily * 30.44, 1), 'breakdown': breakdown}
