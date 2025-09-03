from models.database import db
from models.growing_plant import GrowingPlant
from models.seed_inv import SeedInv
from models.plant_inv import PlantInv
from models.room import Room
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
    room_id = db.Column(db.Integer, db.ForeignKey('room.id', ondelete='SET NULL'), nullable=True)
    is_admin = db.Column(db.Boolean, default=False) # Deny new users administrative permissions

    # Relationships

    # User plant record
    plant_records = db.relationship('UserPlantRecord', back_populates='user', cascade='all, delete-orphan')
    # Growing plants
    growing_plants = db.relationship('GrowingPlant', back_populates='user', cascade='all, delete-orphan')
    # Room
    room = db.relationship('Room', foreign_keys=[room_id], post_update=True)
    owned_room = db.relationship('Room', back_populates='owner', foreign_keys='Room.owner_id', cascade='all, delete-orphan')
    # Messages
    messages = db.relationship('ChatMessage', back_populates='user', cascade='all, delete-orphan')
    # Inventory
    seed_inventories = db.relationship('SeedInv', back_populates='user', cascade='all, delete-orphan')
    plant_inventories = db.relationship('PlantInv', back_populates='user', cascade='all, delete-orphan')
    # Seeds through Seed inventory
    seeds = db.relationship('Seed', secondary='user_seed_inv', back_populates='users')

    # Password hashing to improve user security
    def hash_password(self, password):
        self.password_hash = generate_password_hash(password)
        return

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def add_plant(self, plant, value=None):
        """Add a plant to User's inventory"""
        inv_entry = PlantInv(
            user_id=self.id,
            plant_id=plant.id,
            value=value if value is not None else 0
        )
        db.session.add(inv_entry)

    def remove_plant(self, plant_entry):
        """Remove a plant from User's inventory"""
        if plant_entry in self.plant_inventories:
            db.session.delete(plant_entry)

    def add_seed(self, seed, quantity=1):
        """Add a seed to User's inventory"""
        # Check for existing inventory entry
        inv_entry = SeedInv.query.filter_by(user_id=self.id, seed_id=seed.id).first()

        if inv_entry:
            # Add quantity to existing inventory entry
            inv_entry.quantity += quantity
        else:
            # Create a new inventory entry
            inv_entry = SeedInv(self.id, seed.id, quantity)
            db.session.add(inv_entry)
            if seed not in self.seeds:
                self.seeds.append(seed)
    
    def remove_seed(self, seed):
        """Remove a seed from User's inventory"""
        if seed in self.seeds:
            inv_entry = SeedInv.query.filter_by(
                user_id=self.id,
                seed_id=seed.id
            ).first()
            if inv_entry:
                inv_entry.quantity -= 1
                if inv_entry.quantity <= 0:
                    self.seeds.remove(seed)
                    db.session.delete(inv_entry)
                return True
        return False


    def plant_seed(self, seed_id):
        """Plant a seed and start growing it"""

        seed = GrowingPlant(user_id=self.id, seed_id=seed_id)
        db.session.add(seed)
        db.session.commit()
        return seed
    
    def get_growing_plants(self):
        """Get all plants this user is growing"""
        query = GrowingPlant.query.filter_by(user_id=self.id)
        
        return query.all()
    
    def get_room(self):
        """Get the room the user is currently in"""
        return self.room
    
    def leave_room(self):
        """Leave the room the user is currently in"""
        if self.room:
            room = Room.query.get(self.room_id)
            is_owner = room and room.owner == self

            self.room_id = None

            if room:
                # If User is owner, close room
                if is_owner:
                    db.session.delete(room)
                # Delete room if it is empty after User leaves
                elif not room.members:
                    db.session.delete(room)

            db.session.commit()
    
    def format_dict(self):
        """Format User object to a dictionary for sending user data over HTTP/API endpoints"""
        return {
            'ID': self.id,
            'Username': self.username,
            'E-Mail': self.email,
            'Date Registered': self.date_registered,
            'Currency': self.currency
        }

    def __repr__(self):
        return f"<User {self.username}>"