from . import db #'.'->current python package, no filename because it is from __init__.py
from flask_login import UserMixin # Related to login system of users
from sqlalchemy.sql import func
#* This is the file in which the database models will be created

# Create User class:
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note') #NOTE: for relationship, use class name (including capital letters)

# Create Notes class:
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) #NOTE: for foreign key, use lower-case letters