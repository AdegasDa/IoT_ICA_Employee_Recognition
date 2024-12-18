from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import bcrypt

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key = True)
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


def get_user_info(email):
    res = User.query.filter_by(email=email).first()
    
    if res:
        return res

    return None