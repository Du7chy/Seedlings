from models.database import db
from random import choices

class Seed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    cost = db.Column(db.Integer, nullable=False)
    min_time = db.Column(db.Integer, nullable=False) # Range of time the seed will take to grow in seconds
    max_time = db.Column(db.Integer, nullable=False)

    # Relationships

    # Plants through loot table
    loot_table = db.relationship('LootTable', back_populates='seed', cascade='all, delete-orphan')


    def __init__(self, name, description, cost,  min_time, max_time):
        self.name = name
        self.description = description
        self.cost = cost
        self.min_time = min_time
        self.max_time = max_time

    def add_plant_lt(self, plant, weight):
        """Add a plant to this seed's loot table with a given weight"""
        from models.loot_table import LootTable
        loot_entry = LootTable(self.id, plant.id, weight)
        self.loot_table.append(loot_entry)
        return loot_entry
    
    def generate_random_plant(self):
        """Generate a random plant from this seed's loot table"""
        if not self.loot_table:
            raise ValueError(f"Error: No plants found in '{self.name}' loot table")
        
        # Get plants and their respective weights from loot table
        plants = [entry.plant for entry in self.loot_table]
        weights = [entry.weight for entry in self.loot_table]

        # Select random plant from loot table
        random_plant = choices(plants, weights=weights, k=1)[0]
        return random_plant