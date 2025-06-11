import argparse
from pathlib import Path
import sys

# Get the project root directory
ROOT = Path(__file__).resolve().parent.parent

# Add to Python path
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import create_app
from models.database import db
from models.plant import Plant
from models.seed import Seed

RARITIES = ['common', 'uncommon', 'rare', 'epic', 'legendary',]

def add_plant():
    """Interactive function to add 
    new plants to the database"""
    name = input('Plant name: ')
    while Plant.query.filter_by(name=name).first():
        print(f'Plant {name} already exists!')
        name = input('Plant name: ')
    
    rarity = input('Plant rarity: ').lower()
    while rarity not in RARITIES:
        print("Invalid input! Rarity doesn't exist")
        rarity = input('Plant rarity: ').lower()

    min_value = int(input('Minimum sell value: '))
    while min_value < 0:
        print('Plant cannot sell for less than $0!')
        min_value = int(input('Minimum sell value: '))
    max_value = int(input('Maximum sell value: '))
    while max_value < min_value:
        print('Maximum sell value must be greater than or equal to minimum sell value!')
        max_value = int(input('Maximum sell value: '))

    plant = Plant(name, rarity, min_value, max_value)
    db.session.add(plant)
    db.session.commit()
    return plant

def add_seed():
    """Interactive function to add 
    new seeds to the database"""
    name = input('Seed name: ')
    while Seed.query.filter_by(name=name).first():
        print(f'Seed {name} already exists!')
        name = input('Seed name: ')

    description = input('Description: ')

    cost = int(input('Cost: '))
    while cost < 0:
        print('Seed cannot be less than $0!')
        cost = int(input('Cost: '))

    min_time = int(input('Minimum growth time (seconds): '))
    while min_time <= 0:
        print('Seed must take at least 1 second to grow!')
        min_time = int(input('Minimum growth time (seconds): '))
    max_time = int(input('Maximum growth time (seconds): '))
    while max_time < min_time:
        print('Maximum growth time must be greater than or equal to minimum growth time!')
        max_time = int(input('Maximum growth time (seconds): '))

    seed = Seed(name, description, cost, min_time, max_time)
    db.session.add(seed)
    db.session.commit

    # Add plants to seed loot table

    while True:
        add_plant = input('Add a plant to loot table? (y/n): ').lower()
        if add_plant == 'n':
            break
        elif add_plant != 'n' or add_plant != 'y':
            print('Invalid input! Try again.')
        
        # List all available plants

        plants = Plant.query.all()
        print('\nAvailable plants: ')
        for i, plant in enumerate(plants, 1):
            print(f'{i}. {plant.name} ({plant.rarity})')

        choice = int(input('Choose plant number: ')) - 1
        if 0 <= choice < len(plants):
            weight = float(input('Weight (e.g. 50 for 50%): '))
            seed.add_plant_lt(plants[choice], weight)
            print(f'Added {plants[choice].name} with {weight}% chance to loot table.')
        else:
            print('Invalid input! Try again.')

    db.session.commit()
    return seed

def list_all():
    """List all plants and seeds"""
    print('\nPlants:')
    for plant in Plant.query.all():
        print(f'- {plant.name} ({plant.rarity})\n  ${plant.min_value}-{plant.max_value}')

    print('\nSeeds:')
    for seed in Seed.query.all():
        print(f'- {seed.name} (${seed.cost})\n  Time(s): {seed.min_time}-{seed.max_time}')
        for entry in seed.loot_table:
            print(f'  * {entry.plant.name}: {entry.weight}% chance')

def main():
    # Create the parser
    parser = argparse.ArgumentParser(
        description='Content Adder - Tool for implementing new plants and seeds to database'
    )

    # Arguments
    parser.add_argument(
        'action',
        choices=['add_plant', 'add_seed', 'list'],
        help='Action to perform.'
    )

    parser.add_argument(
        '--rarity', # Optional rarity filter for list command
        choices=RARITIES,
        help='Filter plants by rarity when using list command.'
    )

    # Parse the arguments
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        if args.action == 'list':
            if args.rarity:
                # Filter plants by rarity
                plants = Plant.query.filter_by(rarity=args.rarity).all()
                print(f'\nPlants ({args.rarity}):')
                for plant in plants:
                    print(f'- {plant.name}\n  ${plant.min_value}-{plant.max_value}')
            else:
                list_all()
        elif args.action == 'add_plant':
            plant = add_plant()
            print(f"\nAdded plant successfully:")
            print(f"- Name: {plant.name}")
            print(f"- Rarity: {plant.rarity}")
            print(f"- Value: ${plant.min_value}-{plant.max_value}")
        else:
            seed = add_seed()
            print(f"\nAdded seed packet successfully:")
            print(f"- Name: {seed.name}")
            print(f"- Cost: ${seed.cost}")
            print("- Plants:")
            for entry in seed.loot_table:
                print(f"  * {entry.plant.name}: {entry.weight}% chance")

if __name__ == "__main__":
    main()
        