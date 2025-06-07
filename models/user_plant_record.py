from models.database import db
from datetime import datetime
import pytz

class UserPlantRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    plant_id = db.Column(db.Integer, db.ForeignKey('plant.id', ondelete='CASCADE'), nullable=False)
    times_grown = db.Column(db.Integer, default=0)
    first_discovered = db.Column(db.DateTime)
    last_grown = db.Column(db.DateTime)

    # Relationships

    # User
    user = db.relationship('User', back_populates='plant_records')
    # Plant
    plant = db.relationship('Plant', back_populates='user_records')


    def __init__(self, user_id, plant_id):
        self.user_id = user_id
        self.plant_id = plant_id

    def record(self):
        """Record the number of times an arbitrary 
        user has grown an arbitrary plant"""
        self.times_grown += 1
        self.last_grown = datetime.now(pytz.timezone('Australia/Sydney'))
        db.session.commit()

    @classmethod
    def init_record(cls, user_id, plant_id):
        """Get an existing record or create a new one"""
        record = cls.query.filter_by(user_id=user_id, plant_id=plant_id).first()
        if not record:
            record = cls(user_id, plant_id)
            db.session.add(record)
            db.session.commit()
        return record

