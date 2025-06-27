// Shop Elements
const shopPopup = document.getElementById('shop-popup');
const openShopBtn = document.getElementById('open-shop');
const closeShopBtn = document.querySelector('.close-popup');
const shopTabs = document.querySelectorAll('.shop-tabs .tab-btn');
const seedCatalog = document.querySelector('.seed-catalog');
const plantCatalog = document.querySelector('.plant-catalog');
const buyBtn = document.getElementById('buy-seeds');
const quantityInput = document.getElementById('seed-quantity');
let selectedItemID = null;
let selectedItemPrice = 0;
let currentBalance = 0;

// Update buy button state based on quantity and price
function updateBuyBtn() {
    const quantity = parseInt(quantityInput.value) || 1;
    const totalCost = selectedItemPrice * quantity;

    // Update total cost display
    const costDisplay = document.querySelector('.total-cost');
    if (costDisplay) {
        costDisplay.textContent = `Total: $${totalCost}`;
    }
    
    // Disable button if User can't afford or inputted invalid quantity
    buyBtn.disabled = !selectedItemID || totalCost > currentBalance || quantity < 1;
}

// Get User's current balance from server
async function getBalance() {
    try {
        const response = await fetch('/api/user/balance');
        const data = await response.json();
        currentBalance = data.balance;
        updateBuyBtn();
    } catch (error) {
        console.error('Error getting balance:', error);
        currentBalance = 0; // Fallback to disable buying if balance could not be retrieved
        updateBuyBtn();
    }
}

// Get Item Price
async function getItemPrice(seedID) {
    try {
        const response = await fetch(`/api/shop/items/${seedID}`);
        const data = await response.json();
        selectedItemPrice = data.price;
        updateBuyBtn();
    } catch (error) {
        console.error('Error getting item price:', error);
        selectedItemPrice = Infinity; // Fallback to disable buying if price could not be retrieved
        updateBuyBtn();
    }
}

// Select item to buy
window.selectToBuy = (seedID) => {
    // If item already selected - unselect item
    if (selectedItemID === seedID) {
        selectedItemID = null;
        selectedItemPrice = 0;
    } else {
        selectedItemID = seedID;
        getItemPrice(seedID);
    }

    getBalance(); // Get User's current balance
    updateBuyBtn(); // Update buy button based on new information
    loadBuyTab(); // Refresh selection
}

// Load Buy Tab
async function loadBuyTab() {
    try {
        const response = await fetch('/api/shop/items');
        const items = await response.json();

        seedCatalog.innerHTML = items.map(item => `
            <div class="shop-item ${item.id === selectedItemID ? 'selected' : ''}" onclick="selectToBuy(${item.id})">
                <div class="item-icon">🌱</div>
                <div class="item-info">
                    <div class="item-name">${item.name}</div>
                    <div class="item-details">
                        <div class="price">Price: $${item.price}</div>
                    </div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading buy tab:', error);
    }
}

// Load Sell Tab
async function loadSellTab() {
    try {
        const response = await fetch('/api/inventory');
        const data = await response.json();

        plantCatalog.innerHTML = data.plants.map(plant => `
            <div class="shop-item plant-item" onclick="sellPlant(${plant.id})">
                <div class="item-icon">🌿</div>
                <div class="item-info">
                    <div class="item-name">${plant.name}</div>
                    <div class="item-details">
                        <div class="price">Value: $${plant.value}</div>
                    </div>
                </div>
                <div class="sell-overlay">
                    <span class="sell-icon">💰</span>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading sell tab:', error);
    }
}

// Open/Close Shop Popup
openShopBtn.addEventListener('click', () => {
    shopPopup.style.display = 'block';
    getBalance();
    loadBuyTab()
    loadSellTab();
});

closeShopBtn.addEventListener('click', () => {
    shopPopup.style.display = 'none';
    selectedItemID = null;
    quantityInput.value = '1';
    buyBtn.disabled = true;
});

shopPopup.addEventListener('click', (e) => {
    if (e.target === shopPopup) {
        shopPopup.style.display = 'none';
        selectedItemID = null;
        quantityInput.value = '1';
        buyBtn.disabled = true;
    }
});

// Shop Tab Switching
shopTabs.forEach(tab => {
    tab.addEventListener('click', () => {
        shopTabs.forEach(t => {
            t.classList.remove('active');
            document.querySelectorAll('.shop-content').forEach(content => content.classList.remove('active'));
        });
        tab.classList.add('active');
        document.getElementById(`${tab.dataset.tab}-tab`).classList.add('active');
    });
});

// Update buy button state when quantity changes
quantityInput.addEventListener('input', updateBuyBtn);

// Buy Item
buyBtn.addEventListener('click', async () => {
    if (!selectedItemID) return;

    const quantity = parseInt(quantityInput.value) || 1;
    const totalCost = selectedItemPrice * quantity;

    // Check user can afford the purchase
    if (totalCost > currentBalance) {
        appUtils.jsMessage('You do not have enough money to purchase this!', 'error');
        return;
    }

    try {
        const response = await fetch('/api/shop/buy', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                seed_id: selectedItemID,
                quantity: quantity
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        if (data.success) {
            selectedItemID = null;
            quantityInput.value = '1';
            buyBtn.disabled = true;
            loadBuyTab();
            loadInventory();
            // Update User's balance
            const currencyDisplay = document.querySelector('.currency');
            if (currencyDisplay) {
                currencyDisplay.textContent = `🪙 ${data.balance}`;
            }
            appUtils.jsMessage(data.message, 'success');
        } else {
            appUtils.jsMessage(data.message || 'Failed to buy items.', 'error');
        }
    } catch (error) {
        console.error('Error buying items:', error);
        appUtils.jsMessage('Failed to buy items! Please try again.', 'error');
    }
})

// Sell Plant
window.sellPlant = async (plantID) => {
    try {
        const response = await fetch('/api/shop/sell', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ inv_entry_id: plantID })
        });

        const data = await response.json();
        if (data.success) {
            loadSellTab();
            loadInventory();
            // Update User's balance
            const currencyDisplay = document.querySelector('.currency');
            if (currencyDisplay) {
                currencyDisplay.textContent = `🪙 ${data.balance}`;
            }
            appUtils.jsMessage(data.message, 'success');
        } else {
            appUtils.jsMessage(data.message || 'Failed to sell plant', 'error');
        }
    } catch (error) {
        console.error('Error selling plant:', error);
        appUtils.jsMessage('Failed to sell plant! Please try again.', 'error');
    }
};