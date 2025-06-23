// Initialise global namespace
window.SEEDLINGS = window.SEEDLINGS || {};

// Initialise socket connection
let socket;
if (typeof io !== 'undefined') {
    socket = io(); // Create new client connection to the server

    // Store socket in global namespace
    Object.defineProperty(window.SEEDLINGS, 'socket', {
        value: socket,
        writable: false, 
        configurable: false
    });

    // Global socket error handling
    socket.on('connect_error', (error) => {
        console.error('Socket connection error:', error);
        if (window.appUtils?.jsMessage){
            window.appUtils.jsMessage('Connection error! Please check internet connection and try again.', 'error');
        }

    });

    socket.on('reconnect', (attemptNumber) => {
        console.log('Reconnected to server after', attemptNumber, 'attempts.');
        if (window.appUtils?.jsMessage) {
            window.appUtils.jsMessage('Connection restored!', 'success');
        }

        // Rejoin room on reconnect
        const roomID = window.SEEDLINGS.ROOM_ID;
        if (roomID != null) {
            socket.emit('join', { room_id: String(roomID) });
        }
    });
}

// Initialise room when DOM has loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialise room ID and join socket room
    try {
        const gameContainer = document.querySelector('.game-container');
        if (!gameContainer) return; // User isn't on a room page

        const roomID = gameContainer.dataset.roomID;
        if (!roomID) {
            throw new Error('Game container found but no room ID provided.');
        }

        const parsedID = parseInt(roomID, 10); // Convert room ID string to int
        if (isNaN(parsedID)) {
            throw new Error(`Invalid room ID: ${roomID}`);
        }

        // Set unchangable room ID
        Object.defineProperty(window.SEEDLINGS, 'ROOM_ID', {
            value: parsedID,
            writeable: false,
            configurable: false
        });

        // Join socket room
        if (socket) {
            socket.emit('join', { room_id: String(parsedID) });
        }
    } catch (error) {
        console.error('Error initialising room:', error);
        if (window.gameUtils?.jsMessage) {
            window.gameUtils.jsMessage('Error initialising room! Please refresh the page.', 'error');
        }
        return;
    }

    // Initialise UI elements
    const copyBtn = document.getElementById('copy-code');
    const leaveBtn = document.getElementById('leave-room');

    // Copy join code to clipboard
    if (copyBtn) {
        copyBtn.addEventListener('click', () => {
            const code = copyBtn.previousElementSibling.textContent.trim();
            navigator.clipboard.writeText(code)
                .then(() => appUtils.jsMessage('Join code copied to clipboard!', 'success'))
                .catch(error => {
                    console.error('Failed to copy join code:', error);
                    appUtils.jsMessage('Failed to copy join code.', 'error')
                });
        });
    }

    // Handle leave/close room
    if (leaveBtn) {
        leaveBtn.addEventListener('click', async () => {
            const isOwner = leaveBtn.textContent.trim() === 'Close Room';
            const confirmMessage = isOwner ?
                'Are you sure you want to close this room?':
                'Are you sure you want to leave this room?';
            
            if (confirm(confirmMessage)) {
                try {
                    // Send leave request to HTTP API
                    const response = await fetch(`/api/rooms/${window.SEEDLINGS.ROOM_ID}/leave`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' }
                    });

                    const data = await response.json();
                    if (data.success) {
                        if (socket) {
                            socket.emit('leave', { room_id: String(window.SEEDLINGS.ROOM_ID) });
                        }
                        window.location.href = '/rooms';
                    } else {
                        appUtils.jsMessage(data.message || 'Failed to leave room.', 'error');
                    }
                } catch (error) {
                    console.error('Error leaving room:', error);
                    appUtils.jsMessage('Failed to leave room. Please try again.', 'error');
                }
            }
        });
    }

    // Handle room leave on page unload
    window.addEventListener('beforeunload', () => {
        if (socket && window.SEEDLINGS.ROOM_ID != null) {
            socket.emit('leave', { room_id: String(window.SEEDLINGS.ROOM_ID) });
        }
    });
});