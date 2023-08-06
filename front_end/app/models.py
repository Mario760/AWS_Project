import requests
from flask_login import UserMixin

from flask_sqlalchemy import SQLAlchemy

from . import db

LAMBDA_LOCATION_API = 'https://i3aj0vxx06.execute-api.us-east-1.amazonaws.com/user'

class User(UserMixin, db.Model):
    __tablename__ = 'user'

    username = db.Column(db.String(100), unique=True, primary_key=True)
    password = db.Column(db.String(100))
    user_id = db.Column(db.String(100), unique=True)


    def get_id(self):
        return self.username

    def get_user_id(self):
        return self.user_id
