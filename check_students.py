
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///' + os.path.join(basedir, 'bus_tracking.db'))
db = SQLAlchemy(app)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    required_stop = db.Column(db.String(100))
    assigned_bus_id = db.Column(db.String(10))

with app.app_context():
    students = Student.query.all()
    print(f"Total Students: {len(students)}")
    for s in students:
        print(f"Student: {s.username}, Stop: {s.required_stop}, Bus: {s.assigned_bus_id}")
