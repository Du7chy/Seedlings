from models.database import db
from models.seed import Seed
from datetime import datetime, timedelta
import pytz
import random

class GrowingPlant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    seed_id = db.Column(db.Integer, db.ForeignKey('seed.id', ondelete='CASCADE'), nullable=False)
    planted_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('Australia/Sydney')))
    growth_time = db.Column(db.Integer, nullable=False)
    is_ready = db.Column(db.Boolean, default=False)
    harvested = db.Column(db.Boolean, default=False)

    # Relationships

    # User
    user = db.relationship('User', back_populates='growing_plants')
    # Seed
    seed = db.relationship('Seed', back_populates='growing_plants')


    def __init__(self, user_id, plant_id):
        self.user_id = user_id
        self.plant_id = plant_id

        # Fetch the seed used to get the min/max growth times
        used_seed = Seed.query.get(self.seed_id)

        # Choose the actual growth time for this plant instance
        self.growth_time = random.randint(used_seed.min_time, used_seed.max_time)

    def is_harvestable(self):
        """Check if the plant is ready to harvest"""
        if self.is_ready or self.harvested:
            return self.is_ready
        
        now = datetime.now(pytz.timezone('Australia/Sydney'))
        ready = now >= self.planted_at + timedelta(seconds=self.growth_time)

        if ready:
            self.is_ready = True
            db.session.commit()
        
        return ready
    
    def time_remaining(self):
        """Get the time remaining until fully grown in seconds"""
        if self.is_ready or self.harvested:
            return 0
        
        now = datetime.now(pytz.timezone('Australia/Sydney'))
        harvest_time = self.planted_at + timedelta(minutes=self.growth_time)

        if now >= harvest_time:
            return 0
        
        return (harvest_time - now).total_seconds()

    def harvest(self):
        """Harvest the grown seed and collect and random plant"""
        if self.harvested:
            raise ValueError('This plant has already been harvested!')
        
        if not self.is_harvestable():
            remaining = self.time_remaining()
            raise ValueError(f'Plant is not ready for harvest! {remaining} seconds remaining.')
        
        # Select a random plant from the seeds loot table
        plant = self.seed.generate_random_plant()

        # Record plant for user
        plant.record(self.user_id)

        # Get plant value
        plant_value = random.randint(plant.min_value, plant.max_value)

        # Mark harvested
        self.harvested = True
        db.session.commit()

        return plant, plant_value