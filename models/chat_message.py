from models.database import db
from datetime import datetime
import pytz

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message_content = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Australia/Sydney')))
    room_id = db.Column(db.Integer, db.ForeignKey('room.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)

    # Relationships

    # Room
    room = db.relationship('Room', back_populates='messages')
    # User
    user = db.relationship('User', back_populates='messages')

    def __init__(self, message_content, room_id, user_id):
        self.message_content = message_content
        self.room_id = room_id
        self.user_id = user_id