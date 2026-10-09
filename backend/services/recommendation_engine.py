def generate(d, result):
    recs = []
    def add(title, reason, action, category, priority, impact):
        recs.append({'title': title, 'reason': reason, 'action': action, 'category': category, 'priority': priority, 'impact': impact})
    if d['shower_minutes'] > 8:
        add('Shorten shower time', 'Long showers are a major part of your bathroom estimate.', 'Try reducing each shower by 2–3 minutes.', 'Bathroom', 'HIGH', 'Meaningful bathroom reduction')
    if not d['tap_off_brushing']:
        add('Turn off the tap while brushing', 'Running taps add avoidable daily usage.', 'Wet the brush, turn off the tap, then rinse briefly.', 'Kitchen', 'MEDIUM', 'Small, dependable daily saving')
    if d['laundry_loads_per_week'] > 2 * d['household_size']:
        add('Wash full loads', 'Frequent laundry loads increase the weekly estimate.', 'Combine loads where fabric care allows.', 'Laundry', 'MEDIUM', 'Reduced laundry water per person')
    if d['garden_sessions_per_week'] >= 3:
        add('Water outdoors efficiently', 'Outdoor sessions are contributing to the estimate.', 'Water early, target roots, and use a bucket or drip method.', 'Outdoor', 'HIGH', 'Potential outdoor reduction')
    if not d['leak_aware']:
        add('Check for small leaks', 'Unnoticed leaks can persist between usage activities.', 'Check toilets, taps, and visible pipe connections monthly.', 'Other', 'LOW', 'Avoids ongoing waste')
    if not recs:
        add('Keep your efficient routine', 'Your inputs show several water-aware habits.', 'Review fixtures and habits occasionally.', 'General', 'LOW', 'Maintains efficient use')
    return recs
