from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from datetime import datetime
from werkzeug.middleware.proxy_fix import ProxyFix
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///counter.db'
app.config.from_prefixed_env("APP")
db = SQLAlchemy(app)
socketio = SocketIO(app)

# ProxyFix hinzufügen
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

# Initialisiere ein Lock-Objekt
locks = {}

class Counter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    value = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/')
def index():
    subquery = db.session.query(
        Counter.name,
        func.max(Counter.timestamp).label('latest')
    ).group_by(Counter.name).subquery()

    counters = db.session.query(Counter).join(
        subquery,
        db.and_(
            Counter.name == subquery.c.name,
            Counter.timestamp == subquery.c.latest
        )
    ).all()
    return render_template('index.html', counters=counters)

@app.route('/create', methods=['POST'])
def create():
    name = request.form['name']
    if name:
        new_counter = Counter(name=name)
        db.session.add(new_counter)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<string:name>', methods=['POST'])
def delete(name):
    db.session.query(Counter).filter_by(name=name).delete()
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/counter/<string:name>')
def counter(name):
    counter = db.session.query(Counter).filter_by(name=name).order_by(Counter.timestamp.desc()).first()
    if not counter:
        return redirect(url_for('index'))
    return render_template('counter.html', counter=counter)

@app.route('/history/<int:id>', methods=['GET'])
def history(id):
    counter = db.session.get(Counter, id)
    if not counter:
        return redirect(url_for('index'))
    return render_template('history.html', counter=counter)

@app.route('/history/<string:name>', methods=['POST'])
def history_post(name):
    history_data = Counter.query.filter_by(name=name).order_by(Counter.timestamp).all()
    return jsonify([{'value': entry.value, 'timestamp': entry.timestamp} for entry in history_data])

def get_lock(counter_id):
    if counter_id not in locks:
        locks[counter_id] = threading.Lock()
    return locks[counter_id]

@socketio.on('increment')
def increment(data):
    counter_name = data['name']
    lock = get_lock(counter_name)
    with lock:  # Verwende den Lock, um gleichzeitige Zugriffe zu verhindern
        counter = db.session.query(Counter).filter_by(name=counter_name).order_by(Counter.timestamp.desc()).first()
        if counter:
            new_value = counter.value + 1
            new_counter = Counter(name=counter.name, value=new_value, timestamp=datetime.utcnow())
            db.session.add(new_counter)
            db.session.commit()
            emit('update', {'name': counter_name, 'value': new_value}, broadcast=True)

@socketio.on('decrement')
def decrement(data):
    counter_name = data['name']
    lock = get_lock(counter_name)
    with lock:  # Verwende den Lock, um gleichzeitige Zugriffe zu verhindern
        counter = db.session.query(Counter).filter_by(name=counter_name).order_by(Counter.timestamp.desc()).first()
        if counter and counter.value > 0:
            new_value = counter.value - 1
            new_counter = Counter(name=counter.name, value=new_value, timestamp=datetime.utcnow())
            db.session.add(new_counter)
            db.session.commit()
            emit('update', {'name': counter_name, 'value': new_value}, broadcast=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, allow_unsafe_werkzeug=True, host="0.0.0.0")
