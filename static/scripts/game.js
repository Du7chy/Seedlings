// Game Elements
const seedInventory = document.getElementById('seed-inventory');
const plantInventory = document.getElementById('plant-inventory');
const growingPlants = document.getElementById('growing-plants');
const plantSeedBtn = document.getElementById('plant-seed');
const inventoryTabs = document.querySelectorAll('.tab-btn');
let selectedSeedID = null; // Track which seed User has selected
let growingPlantTimers = new Map(); // Track growth countdown timers for plant displays

// Setup inventory tab switching

inventoryTabs.forEach(tab => {
    tab.addEventListener('click', () => {
        // Remove active class from all tabs and containers
        inventoryTabs.forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.inventory-content').forEach(content => content.classList.remove('active'));

        // Add active class to clicked tab
        tab.classList.add('active');

        // Show corresponding inventory container
        const tabType = tab.getAttribute('data-tab');
        document.getElementById(`inventory-${tabType}`).classList.add('active');
    });
});

// Create a countdown for plant growth, updates every second
function startGrowTimer(plantID, elapsedTime, totalTime) {
    // Clear existing timer (if one exists)
    if (growingPlantTimers.has(plantID)) {
        clearInterval(growingPlantTimers.get(plantID));
    }
    
    let currentElapsed = elapsedTime
    const timer = setInterval(() => {
        currentElapsed++;
        const timeLeft = Math.ceil(Math.max(0, totalTime - currentElapsed));

        // Update the growing plant display
        const timeDisplay = document.querySelector(`#plant-${plantID} .plant-time`);
        const progressBar = document.querySelector(`#plant-${plantID} .progress`);
        if (timeDisplay && progressBar) {
            if (timeLeft === 0) {
                timeDisplay.textContent = 'Ready!';
                progressBar.style.width = '100%';
                // Add harvest button
                const plant = document.querySelector(`#plant-${plantID}`);
                if (plant && !plant.querySelector('.btn-success')) {
                    plant.innerHTML += `
                        <button class="btn btn-success" onclick="harvestPlant(${plantID})">
                            <span class="btn btn-icon">🌿</span> Harvest
                        </button>
                    `;
                }
                // Stop the timer
                clearInterval(timer);
                growingPlantTimers.delete(plantID);
                // Reload growing plants to add ready class
                loadGrowingPlants();
            } else {
                timeDisplay.textContent = `${timeLeft}s`;
                const progress = ((currentElapsed / totalTime) * 100);
                progressBar.style.width = `${progress}%`;
            }
        } else {
            // Plant element no longer exists - clear timer
            clearInterval(timer);
            growingPlantTimers.delete(plantID);
        }
    }, 1000); // Update every second

    growingPlantTimers.set(plantID, timer);
}

// Load and Display Inventory
async function loadInventory() {
    try {
        const response = await fetch('/api/inventory');
        const data = await response.json();

        // Load Seeds
        seedInventory.innerHTML = data.seeds.map(seed => `
                <div class="inventory-item ${seed.id === selectedSeedID ? 'selected': ''}" data-id="${seed.id}" onclick="toggleSeedSelect(${seed.id})">
                    <div class="item-icon">🌱</div>
                    <div class="item-info">
                        <div class="item-name">${seed.name}</div>
                        <div class="item-quantity">x${seed.quantity}</div>
                    </div>
                </div>
        `).join('');

        // Load Plants
        plantInventory.innerHTML = data.plants.map(plant => `
                <div class="inventory-item">
                    <div class="item-icon">🌿</div>
                    <div class="item-info">
                        <div class="item-name">${plant.name}</div>
                    </div>
                </div>
        `).join('');

        // Update plant seed button state
        plantSeedBtn.disable = !selectedSeedID;
    } catch (error) {
        console.error('Error loading inventory:', error);
    }
}

// Load Growing Plants
async function loadGrowingPlants() {
    try {
        const response = await fetch('/api/plants/growing');
        const plants = await response.json();

        growingPlants.innerHTML = plants.map(plant => {
            const isReady = plant.elapsed_time >= plant.growth_time;
            const timeLeft = plant.growth_time - plant.elapsed_time;

            // Start a timer for this plant if one doesn't already exist
            if  (!isReady && !growingPlantTimers.has(plant.id)) {
                startGrowTimer(plant.id, plant.elapsed_time, plant.growth_time);
            }

            return `
                <div id="plant-${plant.id}" class="growing-plant ${isReady ? 'ready' : ''}">
                    <div class="plant-info">
                        <div class="seed-name">${plant.name}</div>
                        <div class="plant-time">
                            ${isReady ? 'Ready!' : `${Math.ceil(timeLeft)}s`}
                        </div>
                    </div>
                    <div class="progress-bar">
                        <div class="progress" style="width: ${(plant.elapsed_time / plant.growth_time * 100)}%"></div>
                    </div>
                    ${isReady ? 
                        `<button class="btn btn-success" onclick="harvestPlant(${plant.id})">
                            <span class="btn-icon">🌿</span> Harvest
                        </button>` :
                        ''
                    }
                </div>
            `;
        }).join('');
    } catch (error) {
        console.error('Error loading growing plants:', error);
    }
}

// Seed Selection Toggle
window.toggleSeedSelect = (id) => {
    // Select seed on click
    // If already selected - unselect
    selectedSeedID = (selectedSeedID === id) ? null : id;
    loadInventory(); // Refresh inventory to show selection
};

// Plant a Seed
plantSeedBtn.addEventListener('click', async () => {
    if (!selectedSeedID) return;

    try {
        const response = await fetch('/api/plants/plant-seed', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ seed_id: selectedSeedID })
        });

        const data = await response.json();
        if (data.success) {
            selectedSeedID = null;
            loadInventory();
            loadGrowingPlants();
            appUtils.jsMessage(data.message, 'success');
        } else {
            appUtils.jsMessage(data.message || 'Failed to plant seed', 'error');
        }
    } catch (error) {
        console.error('Error planting seed:', error);
        appUtils.jsMessage('Failed to plant seed. Please try again.', 'error');
    }
});

// Harvest Plant
window.harvestPlant = async (plantID) => {
    try {
        const response = await fetch(`/api/plants/${plantID}/harvest`, {
            method: 'POST',
        });
        const data = await response.json();

        if (data.success) {
            appUtils.jsMessage(data.message, 'success');
            loadGrowingPlants();
            loadInventory();
        } else {
            appUtils.jsMessage(data.message || 'Failed to harvest plant.', 'error');
        }
    } catch (error) {
        console.error('Error harvesting plant:', error);
        appUtils.jsMessage('Failed to harvest plant. Please try again.', 'error');
    }
};

// Automatically refresh plants and inventory periodically
setInterval(() => {
    loadInventory();
    loadGrowingPlants();
}, 60000); // Every minute

// Refresh on socket reconnect
socket.on('reconnect', () => {
    loadInventory();
    loadGrowingPlants();
});

// Initial Load
loadInventory();
loadGrowingPlants();