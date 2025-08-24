import sqlite3
from flask import Flask, render_template, request, jsonify, g, redirect, url_for, Blueprint
import re

calculator_bp = Blueprint('calculator', __name__, url_prefix='/calculator')
DATABASE = 'history.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with create_app().app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@calculator_bp.route('/')
def index():
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT id, expression, result, memo FROM calculations ORDER BY id DESC')
    history = cur.fetchall()
    return render_template('index.html', history=history)

@calculator_bp.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    expression = data.get('expression', '')
    memo = data.get('memo', '')
    try:
        if not re.match(r'^[0-9+\-*/().\s]*$', expression):
            return jsonify({'error': 'Invalid expression'}), 400
        if not expression.strip():
            return jsonify({'result': ''})
        result = eval(expression)
        db = get_db()
        cur = db.cursor()
        cur.execute('INSERT INTO calculations (expression, result, memo) VALUES (?, ?, ?)', (expression, str(result), memo))
        db.commit()
        return jsonify({'result': result})
    except ZeroDivisionError:
        return jsonify({'error': '0で割ることはできません'}), 400
    except Exception:
        return jsonify({'error': 'Error'}), 400

@calculator_bp.route('/clear_history', methods=['POST'])
def clear_history():
    db = get_db()
    db.execute('DELETE FROM calculations')
    db.commit()
    return redirect(url_for('calculator.index'))

def create_app():
    app = Flask(__name__)
    app.teardown_appcontext(close_connection)
    app.register_blueprint(calculator_bp)
    return app

app = create_app()

@app.cli.command('init-db')
def init_db_command():
    init_db()
    print('Initialized the database.')