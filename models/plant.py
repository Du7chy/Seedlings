from models.database import db
from models.loot_table import LootTable
from models.user_plant_record import UserPlantRecord

class Plant(db.Model):
    id = db.Column(db.Integer, primary_key=True) # Unique identifier for each plant
    name = db.Column(db.String(100), nullable=False)
    rarity = db.Column(db.String(100), nullable=False)
    min_value = db.Column(db.Integer, nullable=False) # Range of value the plant can sell for
    max_value = db.Column(db.Integer, nullable=False)

    # Relationships

    # Seeds through loot table
    seeds = db.relationship('LootTable', back_populates='plant', cascade='all, delete-orphan')
    # User plant record
    user_records = db.relationship('UserPlantRecord', back_populates='plant', cascade='all, delete-orphan')
    # User through inventory
    inventories = db.relationship('PlantInv', back_populates='plant', cascade='all, delete-orphan')


    def __init__(self, name, rarity, min_value, max_value):
        self.name = name
        self.rarity = rarity
        self.min_value = min_value
        self.max_value = max_value

    def get_obtainable_from(self):
        """Get a list of all the seeds that
        contain this plant in its loot table"""
        return [{
            'Seed': entry.seed.name,
            'Chance': (entry.weight / sum(e.weight for e in entry.seed.loot_table)) * 100
        } for entry in self.seeds]

    # Format Plant object to a dictionary for sending data over HTTP/API endpoints
    def format_dict(self):
        return {
            'ID': self.id,
            'Plant': self.name,
            'Rarity': self.rarity,
            'Value Range': f'{self.min_value} - {self.max_value}',
            'Obtainable From': self.get_obtainable_from()
        }