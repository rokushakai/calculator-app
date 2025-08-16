import sqlite3
from flask import Flask, render_template, request, jsonify, g
import re

app = Flask(__name__)
DATABASE = 'history.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.route('/')
def index():
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT id, expression, result, memo FROM calculations ORDER BY id DESC')
    history = cur.fetchall()
    return render_template('index.html', history=history)

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    expression = data.get('expression', '')
    memo = data.get('memo', '')

    try:
        # Pythonのeval関数はセキュリティリスクがあるため、簡単な正規表現でチェック
        if not re.match(r'^[0-9+\-*/.\s]*$', expression):
            return jsonify({'error': 'Invalid expression'}), 400
        
        result = eval(expression)
        
        db = get_db()
        cur = db.cursor()
        cur.execute('INSERT INTO calculations (expression, result, memo) VALUES (?, ?, ?)', (expression, result, memo))
        db.commit()
        
        return jsonify({'result': result})

    except ZeroDivisionError:
        return jsonify({'error': 'ZeroDivisionError'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    init_db()
    app.run(debug=True)