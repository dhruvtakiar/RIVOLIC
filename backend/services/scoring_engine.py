def score(data, result):
    """Transparent prototype score, not a certified efficiency measurement."""
    value = 100
    value -= min(30, max(0, data['shower_minutes'] - 5) * 4)
    value -= min(18, max(0, data['flushes_per_person'] - 5) * 3)
    value -= min(15, data['garden_sessions_per_week'] * 3)
    value -= 8 if not data['tap_off_brushing'] else 0
    value -= 7 if not data['leak_aware'] else 0
    value -= 4 if data['machine_type'] == 'standard' else 0
    return max(0, min(100, round(value)))
