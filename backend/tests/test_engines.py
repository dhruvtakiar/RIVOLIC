import sys; from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from services.consumption_engine import calculate
from services.recommendation_engine import generate
from services.scoring_engine import score
from services.what_if_engine import simulate
base={'household_size':2,'showers_per_person':1,'shower_minutes':10,'baths_per_week':0,'flushes_per_person':5,'dishwasher_loads_per_week':2,'laundry_loads_per_week':3,'garden_sessions_per_week':0,'car_washes_per_month':0,'machine_type':'standard','tap_off_brushing':False,'leak_aware':False}
def test_consumption_total_is_consistent():
 r=calculate(base); assert r['daily_total']==round(sum(r['breakdown'].values()),1)
def test_long_showers_get_recommendation(): assert any(x['title']=='Shorten shower time' for x in generate(base,calculate(base)))
def test_score_is_bounded(): assert 0<=score(base,calculate(base))<=100
def test_what_if_reduces_shower_usage(): assert simulate(base,{'shower_minutes':6})['daily_difference']>0
