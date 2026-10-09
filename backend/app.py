import json, re
from functools import wraps
from flask import Flask, jsonify, request, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from database import get_db, close_db, init_db
from services.consumption_engine import calculate
from services.recommendation_engine import generate
from services.scoring_engine import score
from services.what_if_engine import simulate

def create_app():
    app = Flask(__name__); app.config.from_object(Config)
    CORS(app, supports_credentials=True, origins=['http://localhost:5173'])
    app.teardown_appcontext(close_db); init_db(app)

    @app.errorhandler(404)
    def missing(_): return jsonify(error='Route not found.'), 404
    @app.errorhandler(500)
    def failed(e): app.logger.exception(e); return jsonify(error='Something went wrong. Please try again.'), 500
    def protected(fn):
        @wraps(fn)
        def wrapped(*a, **kw):
            if not session.get('user_id'): return jsonify(error='Please log in to continue.'), 401
            return fn(*a, **kw)
        return wrapped
    def user_payload(user_id):
        row = get_db().execute('SELECT u.id,u.name,u.email,p.household_size,p.location,p.units,p.reduced_motion FROM users u JOIN profiles p ON p.user_id=u.id WHERE u.id=?', (user_id,)).fetchone()
        return dict(row) if row else None
    def number(data, key, low, high, default=None):
        value = data.get(key, default)
        try: value = float(value)
        except (TypeError, ValueError): raise ValueError(f'{key.replace("_", " ").title()} must be a number.')
        if value < low or value > high: raise ValueError(f'{key.replace("_", " ").title()} must be between {low} and {high}.')
        return int(value) if value.is_integer() else value
    def validate_analysis(raw):
        d = {
          'household_size': number(raw, 'household_size', 1, 20), 'showers_per_person': number(raw,'showers_per_person',0,5),
          'shower_minutes': number(raw,'shower_minutes',0,60), 'baths_per_week': number(raw,'baths_per_week',0,20),
          'flushes_per_person': number(raw,'flushes_per_person',0,20), 'dishwasher_loads_per_week': number(raw,'dishwasher_loads_per_week',0,30),
          'laundry_loads_per_week': number(raw,'laundry_loads_per_week',0,50), 'garden_sessions_per_week': number(raw,'garden_sessions_per_week',0,21),
          'car_washes_per_month': number(raw,'car_washes_per_month',0,31), 'machine_type': raw.get('machine_type','standard'),
          'tap_off_brushing': bool(raw.get('tap_off_brushing')), 'leak_aware': bool(raw.get('leak_aware')) }
        if d['machine_type'] not in ('efficient','standard'): raise ValueError('Choose a valid machine type.')
        return d

    @app.post('/api/auth/register')
    def register():
        data=request.get_json(silent=True) or {}; name=data.get('name','').strip(); email=data.get('email','').strip().lower(); password=data.get('password','')
        if not name or not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email) or len(password)<8: return jsonify(error='Enter a name, valid email, and password of at least 8 characters.'),400
        db=get_db()
        try:
            cur=db.execute('INSERT INTO users(name,email,password_hash) VALUES(?,?,?)',(name,email,generate_password_hash(password)))
            db.execute('INSERT INTO profiles(user_id) VALUES(?)',(cur.lastrowid,)); db.commit()
        except Exception:
            return jsonify(error='Unable to create an account with those details.'), 400
        session.clear(); session['user_id']=cur.lastrowid
        return jsonify(user=user_payload(cur.lastrowid), onboarding=True), 201
    @app.post('/api/auth/login')
    def login():
        d=request.get_json(silent=True) or {}; row=get_db().execute('SELECT id,password_hash FROM users WHERE email=?',(d.get('email','').strip().lower(),)).fetchone()
        if not row or not check_password_hash(row['password_hash'],d.get('password','')): return jsonify(error='Invalid email or password.'),401
        session.clear(); session['user_id']=row['id']; return jsonify(user=user_payload(row['id']))
    @app.post('/api/auth/logout')
    def logout(): session.clear(); return jsonify(message='Logged out.')
    @app.get('/api/auth/me')
    @protected
    def me(): return jsonify(user=user_payload(session['user_id']))
    @app.get('/api/profile')
    @protected
    def profile(): return jsonify(user=user_payload(session['user_id']))
    @app.put('/api/profile')
    @protected
    def update_profile():
        d=request.get_json(silent=True) or {}
        try: household=number(d,'household_size',1,20,1)
        except ValueError as e: return jsonify(error=str(e)),400
        name=d.get('name','').strip()
        if not name: return jsonify(error='Name is required.'),400
        get_db().execute('UPDATE users SET name=? WHERE id=?',(name,session['user_id']))
        get_db().execute('UPDATE profiles SET household_size=?,location=?,units=?,reduced_motion=? WHERE user_id=?',(household,d.get('location','').strip(),d.get('units','litres'),int(bool(d.get('reduced_motion'))),session['user_id']));get_db().commit()
        return jsonify(user=user_payload(session['user_id']))
    @app.post('/api/analysis')
    @protected
    def create_analysis():
        try: d=validate_analysis(request.get_json(silent=True) or {})
        except ValueError as e: return jsonify(error=str(e)),400
        result=calculate(d); conservation=score(d,result); recs=generate(d,result); potential=round(result['daily_total'] * sum({'HIGH':.15,'MEDIUM':.07,'LOW':.03}[r['priority']] for r in recs),1)
        largest=max(result['breakdown'],key=result['breakdown'].get); db=get_db()
        cur=db.execute('INSERT INTO analyses(user_id,input_data,daily_total,monthly_total,breakdown,score,potential_reduction,largest_area) VALUES(?,?,?,?,?,?,?,?)',(session['user_id'],json.dumps(d),result['daily_total'],result['monthly_total'],json.dumps(result['breakdown']),conservation,potential,largest))
        for r in recs: db.execute('INSERT INTO analysis_recommendations(analysis_id,title,reason,action,category,priority,impact) VALUES(?,?,?,?,?,?,?)',(cur.lastrowid,r['title'],r['reason'],r['action'],r['category'],r['priority'],r['impact']))
        db.commit(); return analysis_detail(cur.lastrowid)
    def analysis_detail(analysis_id):
        db=get_db(); a=db.execute('SELECT * FROM analyses WHERE id=? AND user_id=?',(analysis_id,session['user_id'])).fetchone()
        if not a: return jsonify(error='Analysis not found.'),404
        value=dict(a); value['input_data']=json.loads(value['input_data']); value['breakdown']=json.loads(value['breakdown']); value['recommendations']=[dict(r) for r in db.execute('SELECT title,reason,action,category,priority,impact FROM analysis_recommendations WHERE analysis_id=?',(analysis_id,))]
        return jsonify(analysis=value)
    @app.get('/api/analysis')
    @protected
    def list_analyses():
        rows=get_db().execute('SELECT id,created_at,daily_total,monthly_total,score,potential_reduction,largest_area FROM analyses WHERE user_id=? ORDER BY id DESC',(session['user_id'],)).fetchall(); return jsonify(analyses=[dict(r) for r in rows])
    @app.get('/api/analysis/<int:analysis_id>')
    @protected
    def get_analysis(analysis_id): return analysis_detail(analysis_id)
    @app.post('/api/analysis/<int:analysis_id>/what-if')
    @protected
    def what_if(analysis_id):
        a=get_db().execute('SELECT input_data FROM analyses WHERE id=? AND user_id=?',(analysis_id,session['user_id'])).fetchone()
        if not a:return jsonify(error='Analysis not found.'),404
        try: return jsonify(simulation=simulate(json.loads(a['input_data']),request.get_json(silent=True) or {}))
        except Exception:return jsonify(error='Use valid scenario values.'),400
    @app.get('/api/dashboard')
    @protected
    def dashboard():
        row=get_db().execute('SELECT * FROM analyses WHERE user_id=? ORDER BY id DESC LIMIT 1',(session['user_id'],)).fetchone()
        return jsonify(user=user_payload(session['user_id']), latest=dict(row) if row else None)
    @app.get('/api/recommendations')
    @protected
    def recommendations():
        rows=get_db().execute('SELECT ar.* FROM analysis_recommendations ar JOIN analyses a ON a.id=ar.analysis_id WHERE a.user_id=? ORDER BY a.id DESC, ar.id',(session['user_id'],)).fetchall();return jsonify(recommendations=[dict(r) for r in rows])
    @app.get('/api/explore')
    def explore(): return jsonify(categories=[{'name':'Practices','items':['Fix visible leaks promptly','Run full laundry loads','Use a bucket for targeted outdoor cleaning']},{'name':'Technologies','items':['Low-flow fixtures','Rainwater harvesting','Greywater reuse','Efficient irrigation','Leak detection']},{'name':'Policies','items':['Look for verified local utility guidance and municipal conservation programs.']}])
    return app

app=create_app()
if __name__=='__main__': app.run(debug=True,port=5000)
