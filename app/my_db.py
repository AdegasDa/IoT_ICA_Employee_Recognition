from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, ForeignKey, Date, Time, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
import bcrypt

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    email = db.Column(db.String(30))
    password = db.Column(db.String(255))
    token = db.Column(db.String(260))
    login = db.Column(db.SmallInteger)
    read_access = db.Column(db.SmallInteger)
    write_access = db.Column(db.SmallInteger)
    register_date = db.Column(db.String(30), nullable=False)


    def __init__(self, email, password, register_date, read_access, write_access, token, login):
        self.email = email
        self.password = password
        self.register_date = register_date
        self.read_access = read_access
        self.write_access = write_access
        self.token = token
        self.login = login


class Employees(db.Model):
    __tablename__ = "employees"

    employee_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    hourly_rate = db.Column(db.Numeric(10, 2), nullable=False)
    day_of_week = db.Column(db.String(80), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    # Relationship to Attendance
    attendance = relationship('Attendance', back_populates='employee', cascade="all, delete-orphan")

    def __init__(self, user_id, first_name, last_name, hourly_rate, day_of_week, start_time, end_time):
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.hourly_rate = hourly_rate
        self.day_of_week = day_of_week
        self.start_time = start_time
        self.end_time = end_time


class Attendance(db.Model):
    __tablename__ = 'attendance'

    attendance_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time_of_arrival = db.Column(db.Time, nullable=False)
    time_of_departure = db.Column(db.Time, nullable=True)
    hours_worked = db.Column(db.Float, nullable=True)
    total_cost = db.Column(db.Float, nullable=True)

    # Relationship to Employee
    employee = relationship('Employees', back_populates='attendance')

    def __init__(self, employee_id, date, time_of_arrival, time_of_departure, hours_worked, total_cost):
        self.employee_id = employee_id
        self.date = date
        self.time_of_arrival = time_of_arrival
        self.time_of_departure = time_of_departure
        self.hours_worked = hours_worked
        self.total_cost = total_cost


def login(email, password):
    user = User.query.filter_by(email = email).first()

    if not user:
        return {"state": 0, "message": "User not found"}

    encoded_password = password.encode('utf-8') 
    stored_hashed_password = user.password.encode('utf-8')
    result = bcrypt.checkpw(encoded_password, stored_hashed_password)
    
    if user and result:
        user.login = 1
        db.session.commit()
        return {"state":1, "message": "Successfully logged in"}
    else:
        return {"state":0, "message": "Invalid email or password"}


def logout(email):
    try:
        user = User.query.filter_by(email = email).first()
        user.login = 0
        db.session.commit()
        return {"state":1, "message": "Successfully logged out"}
    except:
        return {"state":0, "message": "Error"}


def register(email, password, confirm_password):
    user = User.query.filter_by(email=email).first()
    if user:
        return {"state": 0, "message": "User already exists"}
    elif password != confirm_password:
        return {"state": 0, "message": "Both passwords must be the same"}
    else:
        bytes = password.encode('utf-8') 
        salt = bcrypt.gensalt() 
        hashed_password = bcrypt.hashpw(bytes, salt)

        new_user = User(email=email, 
                        password=hashed_password, 
                        token="", 
                        register_date=datetime.now(), 
                        read_access = 0,
                        write_access = 0,
                        login=1) 
        db.session.add(new_user)
        db.session.commit()

        db.session.commit()

        return {"state": 1, "message": "Successfully registered"}


def get_all_users():
    users = User.query.all()

    if users:
        res = [user for user in users]
        res.sort(key=lambda user: user.email)
        return res
    
    return None


def get_user_info(email):
    res = User.query.filter_by(email=email).first()
    
    if res:
        return res

    return None


def get_all_employees():
    employees = Employees.query.all()

    if employees:
        res = [employee for employee in employees]
        res.sort(key=lambda employees: employees.hourly_rate)
        return res
    
    return None


def get_employee(user_id):
    employee = Employees.query.filter_by(user_id = user_id).first()

    if employee:
        return employee
    return None


def add_employee(employee):
    try:
        existing_employee = Employees.query.filter_by(user_id=employee['user_id']).first()
        if existing_employee:
            return {"state": 0, "message": "Employee already exists"}

        new_employee = Employees(
            user_id=employee['user_id'],
            first_name=employee['first_name'],
            last_name=employee['last_name'],
            hourly_rate=employee['hourly_rate'],
            day_of_week=employee['day_of_week'],
            start_time=employee['start_time'],
            end_time=employee['end_time'],
        )

        # Add to the database session
        db.session.add(new_employee)
        db.session.commit()
        return {"state": 1, "message": "Employee added successfully"}
    except Exception as e:
        # Rollback in case of any errors
        db.session.rollback()
        return {"state": 0, "message": f"Error adding employee: {str(e)}"}
    

def update_employee(employee):
    try:
        existing_employee = Employees.query.filter_by(user_id=employee['user_id']).first()

        if not existing_employee:
            return {"state": 0, "message": "Employee does not exist"}

        existing_employee.first_name = employee['first_name']
        existing_employee.last_name = employee['last_name']
        existing_employee.hourly_rate = employee['hourly_rate']
        existing_employee.day_of_week = employee['day_of_week']
        existing_employee.start_time = employee['start_time']
        existing_employee.end_time = employee['end_time']

        db.session.commit()

        return {"state": 1, "message": "Employee updated successfully"}
    except Exception as e:
        db.session.rollback()
        return {"state": 0, "message": f"Error updating employee: {str(e)}"}


def delete_employee(employee_id):
    try:
        existing_employee = Employees.query.filter_by(employee_id=employee_id).first()

        if not existing_employee:
            return {"state": 0, "message": "Employee does not exist"}

        db.session.delete(existing_employee)

        db.session.commit()

        return {"state": 1, "message": "Employee deleted successfully"}
    except Exception as e:
        db.session.rollback()
        return {"state": 0, "message": f"Error deleting employee: {str(e)}"}


def delete_user(id):
    try:
        existing_user = User.query.filter_by(id=id).first()

        if not existing_user:
            return {"state": 0, "message": "User does not exist"}

        db.session.delete(existing_user)

        db.session.commit()

        return {"state": 1, "message": "User deleted successfully"}
    except Exception as e:
        db.session.rollback()
        return {"state": 0, "message": f"Error deleting user: {str(e)}"}
    

def add_user(user_data):
    try:
        # Check if the user already exists by email
        existing_user = User.query.filter_by(email=user_data['email']).first()
        if existing_user:
            return {"state": 0, "message": "User already exists"}

        # Hash the password
        password_bytes = user_data['password'].encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password_bytes, salt)

        # Create a new user instance
        new_user = User(
            email=user_data['email'],
            password=hashed_password,
            register_date=datetime.now(),
            read_access=user_data['read_access'],
            write_access=user_data['write_access'],
            token="",
            login=0  # Default to logged out
        )

        # Add and commit the new user
        db.session.add(new_user)
        db.session.commit()
        return {"state": 1, "message": "User added successfully"}
    except Exception as e:
        db.session.rollback()
        return {"state": 0, "message": f"Error adding user: {str(e)}"}


def update_user(user_id, user_data):
    try:
        # Find the user by ID
        existing_user = User.query.filter_by(id=user_id).first()

        if not existing_user:
            return {"state": 0, "message": "User does not exist"}

        # Update fields if provided
        if 'email' in user_data:
            existing_user.email = user_data['email']

        if 'password' in user_data and user_data['password']:
            password_bytes = user_data['password'].encode('utf-8')
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password_bytes, salt)
            existing_user.password = hashed_password

        if 'read_access' in user_data:
            existing_user.read_access = user_data['read_access']

        if 'write_access' in user_data:
            existing_user.write_access = user_data['write_access']

        # Commit changes
        db.session.commit()
        return {"state": 1, "message": "User updated successfully"}
    except Exception as e:
        db.session.rollback()
        return {"state": 0, "message": f"Error updating user: {str(e)}"}


def add_attendance(attendance):
    try:
        new_attendance = Attendance(
            employee_id=attendance['employee_id'],
            date=attendance['date'],
            time_of_arrival=attendance['time_of_arrival'],
            time_of_departure=attendance['time_of_departure'],
            hours_worked=attendance['hours_worked'],
            total_cost=attendance['total_cost']
        )

        db.session.add(new_attendance)
        db.session.commit()
        return {"state": 1, "message": "Attendance added successfully"}
    except Exception as e:
        # Rollback in case of any errors
        db.session.rollback()
        return {"state": 0, "message": f"Error adding attendance: {str(e)}"}


def update_attendance(employee_id, new_attendance):
    try:
        current_date = datetime.now() 
        
        attendance = Attendance.query.filter_by(employee_id = employee_id, date = current_date).first()
        attendance.time_of_departure = new_attendance['time_of_departure']
        attendance.hours_worked = new_attendance['hours_worked']
        attendance.total_cost = new_attendance['total_cost']

        db.session.commit()

        return {"state": 1, "message": "Attendance added successfully"}
    except Exception as e:
        # Rollback in case of any errors
        db.session.rollback()
        return {"state": 0, "message": f"Error adding attendance: {str(e)}"}


def get_attendances(employee_id):
    attendances = Attendance.query.filter_by(employee_id = employee_id).all()

    if attendances:
        res = [attendance for attendance in attendances]
        res.sort(key=lambda employees: employees.date, reverse=True)
        return res
    
    return None


def get_current_attendance(employee_id):
    attendance = Attendance.query.filter_by(employee_id = employee_id, date = datetime.now, time_of_departure = None).all()

    if attendance:
        return attendance
    
    return None


def get_current_attendances():
    attendances = Attendance.query.filter_by(date = datetime.now(), time_of_departure = None).all()

    if attendances:
        res = [attendance for attendance in attendances]
        res.sort(key=lambda employees: employees.time_of_arrival, reverse=True)
        
        for attendance in res:
            employee = get_employee(attendance.employee_id)
            if (employee):
                attendance.employee_name = "{employee.first_name} {employee.last_name}"

        return res
    
    return None
