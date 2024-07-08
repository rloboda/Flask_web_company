from flask import current_app, jsonify, render_template, current_app as app
import psycopg2
from psycopg2.extras import RealDictCursor

def db_conn():
    config = current_app.config
    conn = psycopg2.connect(
        database=config['DATABASE_NAME'],
        user=config['DATABASE_USER'],
        password=config['DATABASE_PASSWORD'],
        host=config['DATABASE_HOST'],
        port=config['DATABASE_PORT']
    )
    return conn


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/users')
def get_users():
    conn = db_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute('SELECT * FROM users')
    users = cur.fetchall()

    cur.close()
    conn.close()
    
    return jsonify(users)