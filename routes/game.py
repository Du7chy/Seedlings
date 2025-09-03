from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models.database import db
from models.seed import Seed
from models.growing_plant import GrowingPlant
from models.user_plant_record import UserPlantRecord
from models.plant_inv import PlantInv
from models.seed_inv import SeedInv
from datetime import datetime, timezone

game = Blueprint('game', __name__)

@game.route('/api/inventory', methods=['GET'])
@login_required
def get_inv():
    """Get the all items in the User's inventory (seeds and plants)"""
    # Get User's seeds with quantities
    seed_inv = []
    for seed in current_user.seeds:
        inv_entry = SeedInv.query.filter_by(
            user_id=current_user.id,
            seed_id=seed.id
        ).first()
        if inv_entry:
            seed_inv.append({
                'id': seed.id,
                'name': seed.name,
                'quantity': inv_entry.quantity
            })

    # Get User's plants
    plant_inv = [{
        'id': inv_entry.id,
        'plant_id': inv_entry.plant_id,
        'name': inv_entry.plant.name,
        'value': inv_entry.value
    } for inv_entry in current_user.plant_inventories]

    return jsonify({
        'seeds': seed_inv,
        'plants': plant_inv
    })

@game.route('/api/plants/growing', methods=['GET'])
@login_required
def get_growing():
    """Get all of User's growing plants"""
    if not current_user.room_id:
        return jsonify([])
    
    growing = GrowingPlant.query.filter_by(
        user_id=current_user.id,
    ).all()

    now = datetime.now(timezone.utc)
    plants = []

    for plant in growing:
        planted_at = plant.planted_at
        if not planted_at.tzinfo:
            planted_at = planted_at.replace(tzinfo=timezone.utc)

        elapsed = (now - planted_at).total_seconds()
        plants.append({
            'id': plant.id,
            'name': plant.seed.name,
            'growth_time': plant.growth_time,
            'elapsed_time': elapsed
        })
    
    return jsonify(plants)

@game.route('/api/plants/plant-seed', methods=['POST'])
@login_required
def plant_seed():
    """Plant and start growing User's selected seed"""
    if not current_user.room_id:
        return jsonify({'success': False, 'message': "You must be in a room to plant a seed!"})
    
    seed_id = request.json.get('seed_id')
    if not seed_id:
        return jsonify({'success': False, 'message': "No seed selected"})
    
    # Check if User has the seed
    seed = Seed.query.get(seed_id)
    if not seed or seed not in current_user.seeds:
        return jsonify({'success': False, 'message': f"You do not have any {seed.name}s!"})
    
    grow = GrowingPlant(
        user_id=current_user.id,
        seed_id=seed.id
    )

    # Consume planted seed
    if not current_user.remove_seed(seed):
        return jsonify({'success': False, 'message': f"You do not have any {seed.name}s!"})
    
    db.session.add(grow)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f"Planted {seed.name}",
        'growth_time': grow.growth_time
    })

@game.route('/api/plants/<int:plant_id>/harvest', methods=['POST'])
@login_required
def harvest(plant_id):
    """Harvest a User's fully grown plant"""
    plant = GrowingPlant.query.get_or_404(plant_id)

    # Check ownership
    if plant.user_id != current_user.id:
        return jsonify({'success': False, 'message': "This is not your plant!"})
    
    # Check if ready
    if not plant.is_harvestable():
        return jsonify({'success': False, 'message': "This plant is not ready to be harvested!"})
    
    # Select random plant and value from seed loot table
    try:
        ran_plant, value = plant.harvest()

        # Add plant to User's inventory
        current_user.add_plant(ran_plant, value)

        # Update User's plant record
        record = UserPlantRecord.init_record(current_user.id, ran_plant.id)
        record.record()

        # Remove seed from growing plants
        db.session.delete(plant)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'You collected a {ran_plant.name} [{ran_plant.rarity}]!',
            'plant': {
                'id': ran_plant.id,
                'name': ran_plant.name,
                'value': value
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@game.route('/api/user/balance', methods=['GET'])
@login_required
def get_balanced():
    """Get User's current balance"""
    return jsonify({
        'balance': current_user.currency
    })

@game.route('/api/shop/items', methods=['GET'])
@login_required
def get_shop_items():
    """Get all items sold in the shop"""
    try:
        seeds = Seed.query.all()
        return jsonify([
            {
                'id': seed.id,
                'name': seed.name,
                'price': seed.cost
            } for seed in seeds
        ])
    except Exception as e:
        return jsonify([]), 500
    
@game.route('/api/shop/items/<int:seed_id>')
@login_required
def get_selected_item(seed_id):
    """Get data for selected shop item"""
    seed = Seed.query.filter_by(id=seed_id).first()
    return jsonify({
        'id': seed.id,
        'name': seed.name,
        'price': seed.cost
    })

@game.route('/api/shop/buy', methods=['POST'])
@login_required
def buy_items():
    """Buy selected item from the shop"""
    seed_id = request.json.get('seed_id')
    quantity = request.json.get('quantity', 1)

    if not seed_id:
        return jsonify({'success': False, 'message': "No seed selected!"})
    
    seed = Seed.query.get(seed_id)
    if not seed:
        return jsonify({'success': False, 'message': "Seed does not exist!"})
    
    # Check User can afford purchase
    total_cost = seed.cost * quantity
    if current_user.currency < total_cost:
        return jsonify({'success': False, 'message': f"You cannot afford x{quantity} {seed.name}(s)!"})
    
    # Add purchased items to inventory
    current_user.add_seed(seed, quantity=quantity)

    # Change User's balance
    current_user.currency -= total_cost
    db.session.commit()

    return jsonify({
        'success': True ,
        'message': f"You bought x{quantity} {seed.name}(s)!",
        'balance': current_user.currency
    })

@game.route('/api/shop/sell', methods=['POST'])
@login_required
def sell_item():
    """Sell a selected item from User's inventory"""
    inv_entry_id = request.json.get('inv_entry_id')
    if not inv_entry_id:
        return jsonify({'success': False, 'message': "No plant selected!"})
    
    try:
        # Find the specific plant in User's inventory
        plant = PlantInv.query.options(db.joinedload(PlantInv.plant)).filter_by(
            id=inv_entry_id,
            user_id=current_user.id
        ).first()

        if not plant:
            return jsonify({'success': False, 'message': "You do not have this plant!"})
        
        # Add plant value to balance
        current_user.currency += plant.value
        # Remove plant from User's inventory
        current_user.remove_plant(plant)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f"You sold {plant.plant.name} [{plant.plant.rarity}] for ${plant.value}!",
            'balance': current_user.currency
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})