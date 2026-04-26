from app import db, User, Student, Parent, Driver, Bus, Notification, Stop, AdminProfile, app
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

def seed_db():
    with app.app_context():
        print(f"DEBUG: Using database at {app.config['SQLALCHEMY_DATABASE_URI']}")
        # 1. Clear existing
        db.drop_all()
        db.create_all()

        # 2. Add Sample Buses (Matching Select Bus UI)
        b1 = Bus(id='1', name='Bus 1', route_from='Main Gate', route_to='College', route_name='Route A — Main Campus', status='Moving', capacity=60, occupancy=42)
        b2 = Bus(id='2', name='Bus 2', route_from='Station', route_to='North Wing', route_name='Route B — North Wing', status='Stopped', capacity=60, occupancy=10)
        b3 = Bus(id='3', name='Bus 3', route_from='Mall', route_to='South Gate', route_name='Route C — South Gate', status='Delayed', capacity=60, occupancy=5)
        db.session.add_all([b1, b2, b3])
        db.session.flush()

        # Add stops for Bus 1
        s1 = Stop(name='GSSS Simha Subbamahalakshmi First Grade College - ssfgc Mysuru', bus=b1, pickup_time='8:00 AM')
        s2 = Stop(name='Metagalli', bus=b1, pickup_time='8:15 AM')
        s3 = Stop(name='KRS Road', bus=b1, pickup_time='8:30 AM')
        s4 = Stop(name='Main Gate', bus=b1, pickup_time='8:45 AM')
        db.session.add_all([s1, s2, s3, s4])

        # 3. Add Sample Student
        u_student = User(username='student', password='123', role='student', approved=True, email='student@college.edu', phone='9876543210')
        db.session.add(u_student)
        db.session.flush()
        sp = Student(username='student', required_stop='Campus Hub', parent_name='Parent User', is_absent=False)
        db.session.add(sp)

        # 4. Add Sample Parent
        u_parent = User(username='parent', password='123', role='parent', approved=True, email='parent@home.com', phone='8887776665')
        db.session.add(u_parent)
        db.session.flush()
        pp = Parent(user_id=u_parent.id, student_name='student')
        db.session.add(pp)

        # 5. Add Sample Driver
        u_driver = User(username='driver', password='123', role='driver', approved=True, email='driver1@bus.com', phone='1112223334')
        db.session.add(u_driver)
        db.session.flush()
        dp = Driver(user_id=u_driver.id, assigned_bus='1')
        db.session.add(dp)

        # 6. Add admin account
        u_admin = User(username='Principal', password='admin@123', role='admin', approved=True)
        db.session.add(u_admin)
        db.session.flush()
        # Add Admin details
        ap = AdminProfile(user_id=u_admin.id, department='General Administration')
        db.session.add(ap)
        
        # 7. Add sample notification
        n1 = Notification(message="Bus 1 is running 5 minutes late due to traffic at Bogadi Circle.", sender="Principal")
        db.session.add(n1)

        db.session.commit()
        print("Database re-initialized: Admin table created and seeded.")

if __name__ == '__main__':
    seed_db()
