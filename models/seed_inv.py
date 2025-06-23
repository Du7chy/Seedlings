from models.database import db

class SeedInv(db.Model):
    __tablename__ = 'user_seed_inv' # Set a specific tablename instead of setting default
    user_id = db.Column(db.String(36), db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    seed_id = db.Column(db.Integer, db.ForeignKey('seed.id', ondelete='CASCADE'), primary_key=True)
    quantity = db.Column(db.Integer, default=1, nullable=False)

    # Relationships

    # User
    user = db.relationship('User', back_populates='seed_inventories')
    # Seeds
    seed = db.relationship('Seed', back_populates='inventories')

    def __init__(self, user_id, seed_id, quantity=1):
        self.user_id = user_id
        self.seed_id = seed_id
        self.quantity = quantity
    
    def format_dict(self):
        return {
            'user_id': self.user_id,
            'seed_id': self.seed_id,
            'seed_name': self.seed.name,
            'quantity': self.quantity
        }