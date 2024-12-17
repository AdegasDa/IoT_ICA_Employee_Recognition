from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import bcrypt

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"
    user_id = db.Column(db.BigInteger, primary_key = True)
    user_email = db.Column(db.String(50))
    user_password = db.Column(db.String(255))
    user_register_date = db.Column(db.String(30), nullable=False)
    token = db.Column(db.String(255))
    read_access = db.Column(db.SmallInteger)
    write_access = db.Column(db.SmallInteger)
    login = db.Column(db.Integer)


    def __init__(self, user_email, user_password, user_register_date, read_access, write_access, token, login):
        self.user_email = user_email
        self.user_password = user_password
        self.user_register_date = user_register_date
        self.read_access = read_access
        self.write_access = write_access
        self.token = token
        self.login = login
