from .consumption_engine import calculate
def simulate(saved_input, changes):
    current = calculate(saved_input)
    scenario = {**saved_input, **{k:v for k,v in changes.items() if k in saved_input}}
    updated = calculate(scenario)
    return {'current_daily': current['daily_total'], 'scenario_daily': updated['daily_total'], 'daily_difference': round(current['daily_total'] - updated['daily_total'], 1), 'monthly_difference': round((current['daily_total'] - updated['daily_total']) * 30.44, 1), 'scenario_breakdown': updated['breakdown']}
