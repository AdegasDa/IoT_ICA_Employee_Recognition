from flask import Flask, url_for,render_template, request, redirect, session, jsonify

from datetime import datetime
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from functools import wraps
from decimal import Decimal

from .config import config 
from . import my_db, pb


db = my_db.db

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = config.get('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
app.secret_key = config.get('APP_SECRET_KEY')
db.init_app(app)

def login_is_required(function):
    @wraps(function) 
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/")
        else:
            return function(*args, **kwargs)
    
    return wrapper


def admin_is_required(function):
    @wraps(function) 
    def wrapper(*args, **kwargs):
        if str(session['user_id']) != config.get("GOOGLE_ADMIN_ID"):
            return redirect("/index")
        else:
            return function(*args, **kwargs)
    
    return wrapper

 
@app.route("/", methods = ["GET", "POST"])
def signin():
    return render_template("signin.html")


@app.route("/signup", methods = ["GET"])
def signup():
    return render_template("signup.html")


@app.route("/index", methods = ["GET", "POST"])
@login_is_required
def index():
    is_admin = str(session['user_id']) == config.get("GOOGLE_ADMIN_ID")
    user = my_db.get_user_info(session['user_email'])

    attendances = my_db.get_current_attendances()

    return render_template("/index.html", is_admin = is_admin, user = user, attendances = attendances)


@app.route("/attendance", methods = ["GET", "POST"])
@login_is_required
def attendance():
    is_admin = str(session['user_id']) == config.get("GOOGLE_ADMIN_ID")
    user = my_db.get_user_info(session['user_email'])
    employee = my_db.get_employee(user.id)
    attendances = my_db.get_attendances(employee.employee_id)
    employee_name = employee.first_name + " " + employee.last_name
    employees = my_db.get_all_employees()
    employees.remove(employee)
    employees.insert(0,employee)

    return render_template("/attendance.html",employees=employees, employee_for_day=employee,employee_name = employee_name, is_admin = is_admin, user = user, attendances = attendances)


@app.route("/attendance/<user_id>", methods = ["GET", "POST"])
@login_is_required
@admin_is_required
def attendance_admin(user_id):
    is_admin = str(session['user_id']) == config.get("GOOGLE_ADMIN_ID")
    user = my_db.get_user_info(session['user_email'])
    employees = my_db.get_all_employees()
    employee = my_db.get_employee(int(user_id))
    attendances = my_db.get_attendances(int(employee.employee_id))
    employee_name = employee.first_name + " " + employee.last_name
    employees.remove(employee)
    employees.insert(0,employee)

    return render_template("/attendance.html",employee_for_day = employee,employees=employees,employee_name = employee_name, is_admin = is_admin, user = user, attendances = attendances)


@app.route("/admin", methods = ["GET", "POST"])
@login_is_required
@admin_is_required
def admin():
    is_admin = str(session['user_id']) == config.get("GOOGLE_ADMIN_ID")
    employees_data = my_db.get_all_employees()
    if employees_data:
        employees = employees_data
    else:
        employees = []
    user = my_db.get_user_info(session['user_email'])
    users = my_db.get_all_users()

    return render_template("/admin.html", employees = employees, is_admin = is_admin, user = user, users = users)


@app.route("/admin-users", methods = ["GET", "POST"])
@login_is_required
@admin_is_required
def admin_users():
    is_admin = str(session['user_id']) == config.get("GOOGLE_ADMIN_ID")
    users = my_db.get_all_users()
    user = my_db.get_user_info(session['user_email'])

    return render_template("/admin_users.html", users = users, is_admin = is_admin, user = user)


@app.route("/add/user", methods=["POST"])
@login_is_required
@admin_is_required
def add_user():
    try:
        # Retrieve form data
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm-password")
        read_access = 1 if request.form.get("read_access") else 0
        write_access = 1 if request.form.get("write_access") else 0

        # Validate password confirmation
        if password != confirm_password:
            return "Passwords do not match", 400

        # Prepare user data
        user_data = {
            "email": email,
            "password": password,
            "read_access": read_access,
            "write_access": write_access
        }

        # Call the database helper to add the user
        result = my_db.add_user(user_data)

        # Check the result
        if result["state"] == 1:
            return redirect(url_for('admin_users'))
        else:
            print("Error Adding User:", result)
            return "Error Adding User", 400

    except Exception as e:
        print(f"Exception in add_user: {str(e)}")
        return "Internal Server Error", 500

@app.route("/create/attendance/<employee_id>", methods=["POST", "GET"])
def create_attendance(employee_id):
    employee = my_db.get_employee_with_employee_id(int(employee_id))
    
    attendance = request.json

    attendance["employee_id"] = int(employee.employee_id) 
    attendance["date"] = datetime.strptime(attendance["date"], "%Y-%m-%d").date() 
    attendance["time_of_arrival"] = datetime.strptime(attendance["time_of_arrival"], "%H:%M:%S").time() 

    result = my_db.add_attendance(attendance)

    if result["state"] == 1:
            return jsonify({"state": 1, "message": "Attendance created successfully"})
    else:
        return jsonify({"state": 0, "message": result["message"]})
    

@app.route("/update/attendance/<employee_id>", methods=["POST", "GET"])
def update_attendance(employee_id):
    employee = my_db.get_employee_with_employee_id(int(employee_id))
    current_attendance = my_db.get_current_attendance(int(employee_id))

    attendance = request.json

    attendance["time_of_departure"] = datetime.now().time() 

    time_of_arrival = current_attendance.time_of_arrival

    if attendance["time_of_departure"]:
        date_today = datetime.now().date()
        time_of_arrival_dt = datetime.combine(date_today, time_of_arrival)
        time_of_departure_dt = datetime.combine(date_today, attendance["time_of_departure"])

        delta = time_of_departure_dt - time_of_arrival_dt
        attendance["hours_worked"] = delta.total_seconds() / 3600  # Convert seconds to hours
    else:
        attendance["hours_worked"] = 0.0

    cost = float(Decimal(attendance["hours_worked"]) * Decimal(employee.hourly_rate))
    attendance["total_cost"] = round(cost,2)
    result = my_db.update_attendance(employee_id, attendance)

    if result["state"] == 1:
        return jsonify({"state": 1, "message": "Attendance updated successfully"})
    else:
        return jsonify(result), 400



@app.route("/create/employee", methods=["POST"])
@login_is_required
@admin_is_required
def create_employee():
    user = my_db.get_user_info(request.form['user_email'])
    day_of_week = []
    for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
        if request.form.get(day):
            day_of_week.append(day.capitalize())

    # Collect form data
    employee_data = {
        "first_name": request.form['first_name'],
        "last_name": request.form['last_name'],
        "hourly_rate": float(request.form['hourly_rate']),
        "start_time": datetime.strptime(request.form['arrival_time'], "%H:%M").time(),
        "end_time": datetime.strptime(request.form['departure_time'], "%H:%M").time(),
        "day_of_week": " ".join(day_of_week),
        "user_id": user.id
    }

    # Add employee using the database helper
    result = my_db.add_employee(employee_data)

    # Check result state and provide feedback
    if result["state"] == 1:
        return redirect(url_for('admin'))
    else:
        # Log the error and return a meaningful response
        print("Error Editing Employee:", result)
        return "Error Editing Employee", 400
    

@app.route("/delete/employee/<id>", methods=["POST", "GET"])
@login_is_required
@admin_is_required
def delete_employee(id):
    my_db.delete_employee(int(id))

    return redirect(url_for('admin'))


@app.route("/delete/user/<id>", methods=["POST", "GET"])
@login_is_required
@admin_is_required
def delete_user(id):
    my_db.delete_user(int(id))

    return redirect(url_for('admin'))


@app.route("/edit/user/<id>/<url>", methods=["POST", "GET"])
@login_is_required
@admin_is_required
def edit_user(id,url):
    try:
        # Retrieve form data
        email = request.form.get("email")
        read_access = 1 if request.form.get("read_access") else 0
        write_access = 1 if request.form.get("write_access") else 0

        # Prepare user data
        user_data = {
            "id": int(id),
            "email": email,
            "read_access": read_access,
            "write_access": write_access
        }

        # Call the database helper to update the user
        result = my_db.update_user(id, user_data)

        # Check the result
        if result["state"] == 1:
            return redirect(url_for(url))
        else:
            print("Error Editing User:", result)
            return "Error Editing User", 400

    except Exception as e:
        print(f"Exception in edit_user: {str(e)}")
        return "Internal Server Error", 500



@app.route("/edit/employee", methods=["POST"])
@login_is_required
@admin_is_required
def edit_employee():
    user = my_db.get_user_info(request.form['edit_user_email'])

    day_of_week = []
    for day in ['edit_monday', 'edit_tuesday', 'edit_wednesday', 'edit_thursday', 'edit_friday', 'edit_saturday', 'edit_sunday']:
        if request.form.get(day):
            day = day.split("_")[1]
            day_of_week.append(day.capitalize())

    # Collect form data
    employee_data = {
        "first_name": request.form['edit_first_name'],
        "last_name": request.form['edit_last_name'],
        "hourly_rate": float(request.form['edit_hourly_rate']),
        "start_time": datetime.strptime(request.form['edit_arrival_time'], "%H:%M:%S").time(),
        "end_time": datetime.strptime(request.form['edit_departure_time'], "%H:%M:%S").time(),
        "day_of_week": " ".join(day_of_week),
        "user_id": user.id
    }

    # Add employee using the database helper
    result = my_db.update_employee(employee_data)

    # Check result state and provide feedback
    if result["state"] == 1:
        return redirect(url_for('admin'))
    else:
        # Log the error and return a meaningful response
        print("Error Editing Employee:", result)
        return "Error Editing Employee", 400


@app.route("/logout", methods = ["POST", "GET"])
def logout():
    my_db.logout(session['user_email'])
    session.clear()
    return redirect("/")


@app.route("/login", methods = ["POST"])
def login():
    email = request.form['email']
    password = request.form['password']

    res = my_db.login(email, password)
    if res['state'] == 1:
        user_info = my_db.get_user_info(email)
        if user_info:
            session['user_id'] = user_info.id
            session['user_email'] = user_info.email
            return redirect("/index")
    return redirect("/")


@app.route("/register", methods = ["POST"])
def register():
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm-password']

    res = my_db.register(email, password, confirm_password)
    if (res['state'] == 1):
        user_info = my_db.get_user_info(email)
        if user_info:
            print()
            session['user_id'] = user_info.id
            session['user_email'] = user_info.email
            return redirect("/index")
        return redirect("/signup")
    else:
        return redirect("/signup")


if __name__ == '__main__':
    app.run()
