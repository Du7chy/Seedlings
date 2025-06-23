from models.database import db

class PlantInv(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    plant_id = db.Column(db.Integer, db.ForeignKey('plant.id', ondelete='CASCADE'), nullable=False)
    value = db.Column(db.Integer, nullable=False)

    # Relationships

    # User
    user = db.relationship('User', back_populates='plant_inventories')
    # Plant
    plant = db.relationship('Plant', back_populates='inventories')

    def __init__(self, user_id, plant_id, value):
        self.user_id = user_id
        self.plant_id = plant_id
        self.value = value

    def format_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'plant_id': self.plant_id,
            'plant_name': self.plant.name,
            'value': self.value
        }