from models.database import db
from datetime import datetime
import pytz

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('Australia/Sydney')))
    is_private = db.Column(db.Boolean, default=False)
    join_code = db.Column(db.String(4), unique=True)
    max_members = db.Column(db.Integer, default=10)

    # Relationships

    # User --> Owner of room
    owner_id = db.Column(db.String(36), db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    owner = db.relationship('User', back_populates='owned_room', foreign_keys=[owner_id])
    # User --> Member of room
    members = db.relationship('User', foreign_keys='User.room_id', back_populates='room')
    # Chat messages
    messages = db.relationship('ChatMessage', back_populates='room', lazy=True, cascade='all, delete-orphan')
    # lazy=True loads only when necessary, improves performance 


    def __init__(self, name, is_private, max_members, join_code):
        self.name = name
        self.is_private = is_private
        self.max_members = max_members
        self.join_code = join_code

    def member_count(self):
        """Get current number of members in the room"""
        return len(self.members)
    
    def is_member(self, user):
        """Check if a user is a member of the room"""
        return user.room_id == self.id
    
    def is_owner(self, user_id):
        """Check if a user is the owner of the room"""
        return user_id == self.owner_id
    
    def is_full(self):
        return self.member_count() >= self.max_members
    
    def format_dict(self):
        """Format Room object to a dictionary for sending user data over HTTP/API endpoints"""
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at,
            'is_private': self.is_private,
            'join_code': self.join_code,
            'max_members': self.max_members,
            'owner_id': self.owner_id,
            'owner_name': self.owner.username,
            'member_count': self.member_count(),
            'is_full': self.is_full()
        }