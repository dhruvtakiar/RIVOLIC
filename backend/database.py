import sqlite3
from flask import current_app, g

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA foreign_keys = ON')
    return g.db

def close_db(_=None):
    db = g.pop('db', None)
    if db is not None: db.close()

def init_db(app):
    app.config['DATABASE'].parent.mkdir(exist_ok=True)
    with app.app_context():
        db = get_db()
        with open(app.root_path + '/database/schema.sql', encoding='utf-8') as f:
            db.executescript(f.read())
        db.commit()
