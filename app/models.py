from hashlib import md5
from time import time
from flask import current_app, url_for
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login


class User(UserMixin, db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Class method which finds user from DB by username
    @classmethod
    def find_user_by_username(cls, username):
        return cls.query.filter_by(username=username).first()
    
    # Class method which finds user from DB by email
    @classmethod
    def find_user_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def create_user(cls, **kw):
        obj = cls(**kw)
        username = obj.username
        email = obj.email
        
        if cls.find_user_by_username(username):
            raise ValueError("Username already exists.")
        
        if cls.find_user_by_email(email):
            raise ValueError("Email already exists.")

        user = User(username=username, email=email)
        user.set_password(obj.password_hash)      
        db.session.add(user)
        db.session.commit()
        return user

    def to_dict(self, include_email=False):
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
        }
        return data

    def from_dict(self, data, new_user=False):
        for field in ['username', 'email']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class RssFeed(UserMixin, db.Model):
    __tablename__ = 'rss_feed'
    id = db.Column(db.Integer, primary_key=True)
    search_text = db.Column(db.String(50))
    title = db.Column(db.Text)
    link = db.Column(db.Text)
    published = db.Column(db.String(100))
    description = db.Column(db.Text)
    gid = db.Column(db.Text)
    datetime = db.Column(db.DateTime)