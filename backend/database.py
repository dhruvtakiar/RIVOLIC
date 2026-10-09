import re
import sqlite3
from pathlib import Path
from flask import current_app, g

try:
    import psycopg
    from psycopg.rows import dict_row
except ImportError:  # Allows local SQLite-only use until production dependencies are installed.
    psycopg = None
    dict_row = None

class PostgresConnection:
    """Small compatibility layer so application queries stay parameterized."""
    def __init__(self, url):
        if psycopg is None:
            raise RuntimeError('psycopg is required when DATABASE_URL is configured.')
        self.connection = psycopg.connect(url, row_factory=dict_row)

    def execute(self, query, params=()):
        return self.connection.execute(re.sub(r'\?', '%s', query), params)

    def commit(self):
        self.connection.commit()

    def close(self):
        self.connection.close()

def using_postgres():
    return bool(current_app.config.get('DATABASE_URL'))

def get_db():
    if 'db' not in g:
        if using_postgres():
            g.db = PostgresConnection(current_app.config['DATABASE_URL'])
        else:
            g.db = sqlite3.connect(current_app.config['DATABASE'])
            g.db.row_factory = sqlite3.Row
            g.db.execute('PRAGMA foreign_keys = ON')
    return g.db

def close_db(_=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db(app):
    with app.app_context():
        if using_postgres():
            schema_path = Path(app.root_path) / 'database' / 'schema_postgres.sql'
        else:
            Path(app.config['DATABASE']).parent.mkdir(exist_ok=True)
            schema_path = Path(app.root_path) / 'database' / 'schema.sql'
        schema = schema_path.read_text(encoding='utf-8')
        db = get_db()
        if using_postgres():
            for statement in (part.strip() for part in schema.split(';')):
                if statement:
                    db.execute(statement)
        else:
            db.executescript(schema)
        db.commit()