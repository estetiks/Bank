from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import bcrypt



db = SQLAlchemy()
salt = bcrypt.gensalt()

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable = False)
    username = db.Column(db.String(25), unique=True, nullable = False)
    email = db.Column(db.String, unique=False, nullable = False)
    password_hash = db.Column(db.String(500), nullable = False)
    balance_RUB = db.Column(db.Float, default=0, nullable=False)
    balance_USD = db.Column(db.Float, default=0, nullable=False)
    balance_EUR = db.Column(db.Float, default=0, nullable=False)
    shares_HL = db.Column(db.Integer, default=0, nullable=False)
    shares_TUBE = db.Column(db.Integer, default=0, nullable=False)

