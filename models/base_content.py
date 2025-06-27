from models.database import db
from models.plant import Plant
from models.seed import Seed
from models.loot_table import LootTable

def base_content():
    """Add base plants, seeds and seed loot tables if they don't exist"""
    base_plants = [
        # Name, Rarity, Minimum Value, Maximum Value
        # Common (100-500)
        ('Daisy', 'common', 100, 150),
        ('Sunflower', 'common', 150, 200),
        ('Mint', 'common', 175, 225),
        ('Clover', 'common', 200, 250),
        ('Basil', 'common', 250, 300),
        ('Lavender', 'common', 300, 400),
        ('Marigold', 'common', 350, 500),
        # Uncommon (500-1000)
        ('Venus Flytrap', 'uncommon', 500, 700),
        ('Chamomile', 'uncommon', 550, 750),
        ('Snapdragon', 'uncommon', 600, 800),
        ('Aloe Vera', 'uncommon', 650, 850),
        ('Thyme', 'uncommon', 700, 900),
        ('Morning Glory', 'uncommon', 750, 950),
        ('Chili Plant', 'uncommon', 800, 1000),
        # Rare (1000-2500)
        ('Bleeding Heart', 'rare', 1000, 1500),
        ('Ghost Orchid', 'rare', 1200, 1700),
        ('Dragon Tree', 'rare', 1400, 1900),
        ('Blue Lotus', 'rare', 1600, 2100),
        ('Moonflower', 'rare', 1800, 2300),
        ('Pitcher Plant', 'rare', 2000, 2500),
        ('Eucalyptus Sapling', 'rare', 2200, 2500),
        # Epic (2500-5000)
        ('Corpse Flower', 'epic', 2500, 3000),
        ('Silver Fern', 'epic', 2800, 3500),
        ('Jade Vine', 'epic', 3100, 4000),
        ('Queen of the Night', 'epic', 3400, 4500),
        ('Baobab Sapling', 'epic', 3700, 4700),
        ('Black Bat Flower', 'epic', 4000, 4800),
        ('Wolffia', 'epic', 4300, 5000),
        # Legendary (5000-25000)
        ('Yggdrasil Sapling', 'legendary', 5000, 12000),
        ('Phoenix Bloom', 'legendary', 8000, 14000),
        ('Lunar Ivy', 'legendary', 12000, 16000),
        ('Chrono Fern', 'legendary', 14000, 18000),
        ('Emberbloom', 'legendary', 17000, 20000),
        ('Crystal Rose', 'legendary', 20000, 22000),
        ('Eternal Sprout', 'legendary', 22000, 25000)
    ]

    for name, rarity, min_value, max_value in base_plants:
        if not Plant.query.filter_by(name=name).first():
            plant = Plant(name, rarity, min_value, max_value)
            db.session.add(plant)

    base_seeds = [
        # Name, Description, Cost, Minimum Growth Time, Maximum Growth Time
        ('Meadow Seed', 'A simple seed from sunny fields. Grows familiar and friendly plants. Perfect for beginners!', 75, 30, 45),
        ('Forest Seed', 'Found in the shade of deep woods. Grows fragrant and leafy flora with a touch of magic.', 200, 45, 60),
        ('Desert Seed', 'Dry and rugged, this seed survives the harshest sun.', 500, 60, 120),
        ('Mystic Seed', 'Rumored to be enchanted. Glows faintly at night.', 1000, 90, 180),
        ('Blooming Seed', 'Packed with colour and life.', 2000, 180, 300),
        ('Nightfall Seed', 'Thrives in moonlight.', 5000, 240, 360),
        ('Ancient Seed', 'Wrapped in timeworn roots. This ancient seed carries echoes of a forgotten world.', 15000, 480, 600),
        ('Wild Seed', "Chaotic and unpredictable. No one knows what will grow - but it's always interesting.", 1500, 60, 300)
    ]

    for name, desc, cost, min_time, max_time in base_seeds:
        if not Seed.query.filter_by(name=name).first():
            seed = Seed(name, desc, cost, min_time, max_time)
            db.session.add(seed)
    
    db.session.commit()

    loot_tables = {
        'Meadow Seed': [ # Min profit: +25 -- Max profit: +625
            # Common (98%)
            ('Daisy', 25), 
            ('Sunflower', 25),
            ('Mint', 20),
            ('Clover', 15),
            ('Basil', 13),
            # Uncommon (2%)
            ('Venus Flytrap', 2)
        ],
        
        'Forest Seed': [ # Min profit: +50 -- Max profit: +650
            # Common (60%)
            ('Basil', 20),
            ('Lavender', 20),
            ('Marigold', 20),
            # Uncommon (40%)
            ('Snapdragon', 15),
            ('Aloe Vera', 15),
            ('Venus Flytrap', 10)
        ],
        
        'Desert Seed': [ # Min profit: -150 -- Max profit: +2000
            # Common (30%)
            ('Marigold', 30),
            # Uncommon (55%)
            ('Thyme', 20),
            ('Chili Plant', 20),
            ('Morning Glory', 15),
            # Rare (15%)
            ('Dragon Tree', 10),  
            ('Pitcher Plant', 5)
        ],
        
        'Mystic Seed': [ # Min profit: -450 -- Max profit: +3500
            # Uncommon (40%)
            ('Morning Glory', 25),
            ('Chamomile', 15),
            # Rare (45%)
            ('Moonflower', 20),
            ('Ghost Orchid', 15),
            ('Blue Lotus', 10),
            # Epic (15%)
            ('Jade Vine', 10),
            ('Queen of the Night', 5)
        ],
        
        'Blooming Seed': [ # Min profit: -1000 -- Max profit: +7800
            # Rare (35%)
            ('Bleeding Heart', 20),
            ('Ghost Orchid', 15),
            # Epic (60%)
            ('Corpse Flower', 25),
            ('Silver Fern', 20),
            ('Jade Vine', 15),
            # Legendary (5%)
            ('Crystal Rose', 5)
        ],

        'Wild Seed': [ # Min profit: -1400 , Max profit: +20500
            # Common (40%)
            ('Daisy', 8),
            ('Mint', 8),
            ('Clover', 8),
            ('Basil', 8),
            ('Marigold', 8),
            # Uncommon (30%)
            ('Venus Flytrap', 6),
            ('Aloe Vera', 6),
            ('Thyme', 6),
            ('Morning Glory', 6),
            ('Chili Plant', 6),
            # Rare (20%)
            ('Ghost Orchid', 4),
            ('Blue Lotus', 4),
            ('Moonflower', 4),
            ('Pitcher Plant', 4),
            ('Dragon Tree', 4),
            # Epic (9%)
            ('Corpse Flower', 3),
            ('Jade Vine', 2),
            ('Black Bat Flower', 2),
            ('Wolffia', 2),
            # Legendary (1%)
            ('Phoenix Bloom', 0.5),
            ('Crystal Rose', 0.5)
        ],

        'Nightfall Seed': [ # Min profit: -1900 -- Max profit: +13000
            # Epic (60%)
            ('Black Bat Flower', 25),
            ('Wolffia', 20),
            ('Jade Vine', 15),
            # Legendary (40%)
            ('Yggdrasil Sapling', 20),
            ('Phoenix Bloom', 10),
            ('Lunar Ivy', 5),
            ('Chrono Fern', 5)
        ],
        
        'Ancient Seed': [ # Min profit: -10000 -- Max profit: +10000
            # Legendary (100%)
            ('Yggdrasil Sapling', 25),
            ('Phoenix Bloom', 20),
            ('Lunar Ivy', 15),
            ('Chrono Fern', 15),
            ('Emberbloom', 15),
            ('Crystal Rose', 10),
            ('Eternal Sprout', 5)
        ]
    }

    for seed_name, drops in loot_tables.items():
        seed = Seed.query.filter_by(name=seed_name).first()
        if not seed:
            print(f'Error: Seed {seed_name} not found!')
            continue

        existing_drops = {(entry.plant_id, entry.weight) for entry in LootTable.query.filter_by(seed_id=seed.id)}

        for plant_name, weight in drops:
            plant = Plant.query.filter_by(name=plant_name).first()
            if not plant:
                print(f'Error: Plant {plant_name} not found!')
                continue

            if (plant.id, weight) not in existing_drops:
                drop = LootTable(seed.id, plant.id, weight)
                db.session.add(drop)

    db.session.commit()