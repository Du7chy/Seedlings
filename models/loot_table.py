from models.database import db

class LootTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seed_id = db.Column(db.Integer, db.ForeignKey('seed.id', ondelete='CASCADE'), nullable=False)
    plant_id = db.Column(db.Integer, db.ForeignKey('plant.id', ondelete='CASCADE'), nullable=False)
    weight = db.Column(db.Integer, nullable=False, default=100) # Percentage probability weight of an arbitrary plant

    # Relationships

    # Seeds
    seed = db.relationship('Seed', back_populates='loot_table')
    # Plants
    plant = db.relationship('Plant', back_populates='seeds')


    def __init__(self, seed_id, plant_id, weight):
        self.seed_id = seed_id
        self.plant_id = plant_id
        self.weight = weight