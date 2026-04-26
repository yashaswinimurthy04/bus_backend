from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
# Allow CORS for the frontend
CORS(app, resources={r"/api/*": {"origins": "*"}})

# PostgreSQL Configuration
# Database Configuration
# Ensure absolute path for database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///' + os.path.join(basedir, 'bus_tracking.db'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), nullable=False) # student, parent, driver, admin
    approved = db.Column(db.Boolean, default=False)
    phone = db.Column(db.String(15))
    email = db.Column(db.String(100))

    # Relationships to profiles
    parent_info = db.relationship('Parent', backref='user', uselist=False, cascade="all, delete-orphan")
    driver_info = db.relationship('Driver', backref='user', uselist=False, cascade="all, delete-orphan")
    admin_info = db.relationship('AdminProfile', backref='user', uselist=False, cascade="all, delete-orphan")

    def to_dict(self):
        data = {
            "id": self.id, 
            "username": self.username, 
            "role": self.role,
            "approved": self.approved
        }
        
        # Merge profile details based on role
        if self.role == 'student':
            student = Student.query.filter_by(username=self.username).first()
            if student:
                data.update({
                    "assigned_stop": student.required_stop,
                    "parent_name": student.parent_name
                })
        elif self.role == 'parent' and self.parent_info:
            data.update({
                "student_name": self.parent_info.student_name
            })
        elif self.role == 'driver' and self.driver_info:
            data.update({
                "assigned_bus": self.driver_info.assigned_bus
            })
        elif self.role == 'admin':
            data.update({"username": self.username})
            if self.admin_info:
                data.update({
                    "department": self.admin_info.department
                })
            
        return data

class Student(db.Model):
    __tablename__ = 'student'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    required_stop = db.Column(db.String(100))
    parent_name = db.Column(db.String(100))

class Parent(db.Model):
    __tablename__ = 'parent'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    full_name = db.Column(db.String(100))
    student_name = db.Column(db.String(100))

class Driver(db.Model):
    __tablename__ = 'driver'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assigned_bus = db.Column(db.String(10))

class AdminProfile(db.Model):
    __tablename__ = 'admin_profile'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    department = db.Column(db.String(100), default="Management")

class Bus(db.Model):
    __tablename__ = 'bus'
    id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    route_from = db.Column(db.String(100))
    route_to = db.Column(db.String(100))
    route_name = db.Column(db.String(100)) # Still keeps combined for legacy
    current_stop = db.Column(db.String(100))
    next_stop = db.Column(db.String(100))
    eta = db.Column(db.String(20))
    speed = db.Column(db.Float, default=0.0)
    lat = db.Column(db.Float, default=12.3382) 
    lng = db.Column(db.Float, default=76.6261)
    driver_name = db.Column(db.String(100))
    status = db.Column(db.String(20), default="Stopped")
    capacity = db.Column(db.Integer, default=50)
    occupancy = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    stops = db.relationship('Stop', backref='bus', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "route_from": self.route_from,
            "route_to": self.route_to,
            "route_name": self.route_name or f"{self.route_from} → {self.route_to}",
            "current_stop": self.current_stop,
            "next_stop": self.next_stop,
            "eta": self.eta,
            "speed": self.speed,
            "lat": self.lat,
            "lng": self.lng,
            "status": self.status,
            "capacity": self.capacity,
            "occupancy": self.occupancy,
            "stops": [s.name for s in self.stops]
        }

class Stop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    pickup_time = db.Column(db.String(20)) # Added for bus timing detail
    bus_id = db.Column(db.String(10), db.ForeignKey('bus.id'), nullable=False)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(500), nullable=False)
    sender = db.Column(db.String(20), default='admin')
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

    def to_dict(self):
        return {
            "id": self.id,
            "message": self.message,
            "sender": self.sender,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }

# API Routes
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')

    # ✅ SPECIAL RULE FOR ADMIN
    if role == 'admin':
        admin_user_env = os.getenv('ADMIN_USERNAME', 'Principal')
        admin_pass_env = os.getenv('ADMIN_PASSWORD', 'admin@123')
        
        if username == admin_user_env and password == admin_pass_env:
            # Check if admin user exists in DB, if not create/sync it
            admin_user = User.query.filter_by(username=admin_user_env, role='admin').first()
            if not admin_user:
                admin_user = User(username=admin_user_env, password=admin_pass_env, role='admin', approved=True)
                db.session.add(admin_user)
                db.session.commit()
            return jsonify({"success": True, "user": admin_user.to_dict()})
        return jsonify({"success": False, "message": "Invalid Admin Credentials"}), 401

    user = User.query.filter_by(username=username, password=password, role=role).first()
    if user:
        if not user.approved and user.role != 'admin':
            return jsonify({"success": False, "message": "Account pending admin approval"}), 403
            
        # ✅ ENFORCE BUS-SPECIFIC DRIVER LOGIN
        if role == 'driver':
            requested_bus = data.get('bus_id')
            if not requested_bus or str(user.driver_info.assigned_bus) != str(requested_bus):
                return jsonify({"success": False, "message": f"Unauthorized: You are not assigned to Bus {requested_bus}"}), 403
                
        return jsonify({"success": True, "user": user.to_dict()})
    return jsonify({"success": False, "message": "Invalid credentials"}), 401

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    role = data.get('role')
    
    # ✅ BLOCK ADMIN SIGNUP
    if role == 'admin':
        return jsonify({"success": False, "message": "Administrator registration is disabled"}), 403

    if User.query.filter_by(username=username).first():
        return jsonify({"success": False, "message": "Username already taken"}), 400

    try:
        new_user = User(username=username, password=data.get('password'), role=role, approved=False)
        db.session.add(new_user)
        db.session.flush()

        if role == 'student':
            profile = Student(
                username=username, 
                required_stop=data.get('assigned_stop'), 
                parent_name=data.get('parent_name')
            )
            db.session.add(profile)
        elif role == 'parent':
            # Validation: Check if there's a student with matching names
            parent_full_name = data.get('full_name')
            target_student_name = data.get('student_name')
            
            # Look for a student whose username matches student_name AND parent_name matches full_name
            student_exists = Student.query.filter_by(username=target_student_name, parent_name=parent_full_name).first()
            
            if not student_exists:
                db.session.rollback()
                return jsonify({"success": False, "message": "Wrong credentials: No matching student record found for these names"}), 401
                
            profile = Parent(user_id=new_user.id, full_name=parent_full_name, student_name=target_student_name)
            db.session.add(profile)
        elif role == 'driver':
            profile = Driver(user_id=new_user.id, assigned_bus=data.get('assigned_bus'))
            db.session.add(profile)

        db.session.commit()
        return jsonify({"success": True, "message": "Signup successful", "user": new_user.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/admin/pending_users', methods=['GET'])
def get_pending_users():
    users = User.query.filter_by(approved=False).all()
    return jsonify([user.to_dict() for user in users])

@app.route('/api/admin/all_users', methods=['GET'])
def get_all_users():
    users = User.query.filter(User.role != 'admin').all()
    return jsonify([user.to_dict() for user in users])

@app.route('/api/admin/approve_user/<int:user_id>', methods=['POST'])
def approve_user(user_id):
    user = User.query.get(user_id)
    if user:
        user.approved = True
        db.session.commit()
        return jsonify({"success": True, "message": f"User {user.username} approved"})
    return jsonify({"success": False, "message": "User not found"}), 404

@app.route('/api/admin/delete_user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"success": True, "message": f"User {user.username} deleted"})
    return jsonify({"success": False, "message": "User not found"}), 404

@app.route('/api/admin/add_bus', methods=['POST'])
def add_bus():
    data = request.json
    try:
        bus_id = data.get('id')
        driver_name = data.get('driver_name')
        route_from = data.get('route_from')
        route_to = data.get('route_to')
        route_name = f"{route_from} → {route_to}"
        
        bus = Bus.query.get(bus_id)
        if not bus:
            bus = Bus(id=bus_id, name=f"Bus {bus_id}", route_from=route_from, route_to=route_to, route_name=route_name, driver_name=driver_name)
        bus.driver_name = driver_name
        
        # 2. Create or Update Driver User
        driver_user = None
        if driver_name:
            existing_user = User.query.filter_by(username=driver_name).first()
            if existing_user and existing_user.role != 'driver':
                return jsonify({"success": False, "message": "Driver name conflicts with existing non-driver account"}), 400
                
            driver_user = existing_user
            if not driver_user:
                # Set automated password during creation to satisfy not-null constraint
                temp_pass = f"bus{bus_id}driver"
                driver_user = User(username=driver_name, password=temp_pass, role='driver', approved=True)
                db.session.add(driver_user)
                db.session.flush()
            
            driver_user.password = f"bus{bus_id}driver"
            
            # Update Driver Profile
            profile = driver_user.driver_info
            if not profile:
                profile = Driver(user_id=driver_user.id)
                db.session.add(profile)
                db.session.flush()
            profile.assigned_bus = bus_id

        # 3. Update Stops
        Stop.query.filter_by(bus_id=bus_id).delete()
        stops_list = data.get('stops', [])
        for stop_name in stops_list:
            if stop_name.strip():
                new_stop = Stop(name=stop_name, bus=bus)
                db.session.add(new_stop)

        db.session.add(bus)
        db.session.commit()
        return jsonify({"success": True, "message": f"Bus {bus_id} and Driver {driver_name} updated"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/notifications', methods=['GET', 'POST'])
def handle_notifications():
    if request.method == 'POST':
        data = request.json
        new_note = Notification(message=data.get('message'), sender=data.get('sender', 'admin'))
        db.session.add(new_note)
        db.session.commit()
        return jsonify({"success": True})
    notes = Notification.query.order_by(Notification.timestamp.desc()).limit(10).all()
    return jsonify([n.to_dict() for n in notes])

@app.route('/api/bus/update_status', methods=['POST'])
def update_bus_status():
    data = request.json
    bus_id = data.get('bus_id')
    bus = Bus.query.get(bus_id)
    if bus:
        if 'status' in data: bus.status = data['status']
        if 'occupancy' in data: bus.occupancy = data['occupancy']
        if 'current_stop' in data: bus.current_stop = data['current_stop']
        if 'next_stop' in data: bus.next_stop = data['next_stop']
        
        db.session.commit()
        return jsonify({"success": True, "bus": bus.to_dict()})
    return jsonify({"success": False, "message": "Bus not found"}), 404

@app.route('/api/buses', methods=['GET'])
def get_buses():
    buses = Bus.query.all()
    return jsonify([bus.to_dict() for bus in buses])

@app.route('/api/buses/<bus_id>', methods=['GET'])
def get_bus(bus_id):
    bus = Bus.query.get(bus_id)
    if bus:
        return jsonify(bus.to_dict())
    return jsonify({"message": "Bus not found"}), 404

@app.route('/api/students', methods=['GET'])
def get_all_students():
    students = Student.query.all()
    return jsonify([{"username": s.username, "required_stop": s.required_stop} for s in students])

@app.route('/api/bus/<bus_id>/students', methods=['GET'])
def get_bus_students(bus_id):
    return jsonify([])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5001, debug=True)
