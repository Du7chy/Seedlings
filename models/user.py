from models.database import db
import uuid
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pytz

class User(db.Model, UserMixin):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4())) # Generate a unique user ID
    username = db.Column(db.String(24), unique=True, nullable=False) 
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    date_registered = db.Column(db.DateTime, default=datetime.now(pytz.timezone('Australia/Sydney'))) # Save time of registration relative to Sydney's timezone
    currency = db.Column(db.Integer, default=100) # Set default currency to 100
    is_admin = db.Column(db.Boolean, default=False) # Deny new users administrative permissions

    # Password hashing to improve user security
    def hash_password(self, password):
        self.password_hash = generate_password_hash(password)
        return

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Format User object to a dictionary for sending user data over HTTP/API endpoints
    def format_dict(self):
        return {
            'ID': self.id,
            'Username': self.username,
            'E-Mail': self.email,
            'Date Registered': self.date_registered,
            'Currency': self.currency
        }

    def __repr__(self):
        return f"<User {self.username}>"