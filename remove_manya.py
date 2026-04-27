import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///' + os.path.join(basedir, 'bus_tracking.db'))
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)

with app.app_context():
    # Remove from Student table
    students = Student.query.filter_by(username='manya').all()
    for s in students:
        db.session.delete(s)
    
    # Remove from User table
    users = User.query.filter_by(username='manya').all()
    for u in users:
        db.session.delete(u)
        
    db.session.commit()
    print("manya removed")
