
import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///' + os.path.join(basedir, 'bus_tracking.db'))
db = SQLAlchemy(app)

class Bus(db.Model):
    id = db.Column(db.String(20), primary_key=True)
    stops = db.relationship('Stop', backref='bus', lazy=True)

class Stop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    bus_id = db.Column(db.String(20), db.ForeignKey('bus.id'))

with app.app_context():
    buses = Bus.query.all()
    print(f"Total Buses: {len(buses)}")
    for b in buses:
        print(f"Bus {b.id}: {len(b.stops)} stops")
        for s in b.stops:
            print(f"  - {s.name}")
