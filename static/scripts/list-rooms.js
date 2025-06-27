document.addEventListener('DOMContentLoaded', function() {
    // Room List Elements
    const roomList = document.getElementById('room-list');
    const searchInput = document.getElementById('room-search');
    const searchBtn = document.getElementById('search-btn');
    const joinBtn = document.getElementById('join-btn');
    const joinPopup = document.getElementById('join-popup');
    const joinCodeInput = document.getElementById('join-code');
    const popupJoinBtn = document.getElementById('popup-join');
    const popupCancelBtn = document.getElementById('popup-cancel');
    const loading = document.getElementById('loading');
    let searchTimeout;

    // Functions

    // Join room by code or ID
    async function joinRoom(roomID = null, joinCode = null) {
        try {
            const response = await fetch('/api/rooms/join', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(roomID ? { room_id: roomID } : { join_code: joinCode })
            });

            const data = await response.json();
            if (data.success) {
                window.location.href = data.redirect;
            } else {
                alert(data.message || 'Failed to join room.')
                if (data.redirect) {
                    window.location.href = data.redirect;
                }
            }
        } catch (error) {
            console.error('Error joining room:', error);
            alert('Failed to join room. Please try again.');
        }
    }

    // Create room cards
    function createRoomCard(room) {
        return `
            <div class="room-card ${room.is_full ? 'full' : ''}">
                <div class="room-card-header">
                    <h3>${room.name}</h3>
                    ${room.is_private ? '<span class="room-private" title="Private Room">🔒</span>' : ''}
                </div>
                <div class="room-card-content">
                    <div class="room-stats">
                        <span title="Members">👥 ${room.member_count}/${room.max_members}</span>
                        <span class="room-owner">Created by ${room.owner_name}</span>
                    </div>
                </div>
                <div class="room-card-actions">
                    <button class="btn btn-primary join-room-btn" 
                            onclick="joinRoom(${room.id})"
                            ${room.is_full ? 'disabled' : ''}>
                        ${room.is_full ? 'Room Full' : 'Join Room'}
                    </button>
                </div>
            </div>
        `;
    }

    // Load and display rooms
    async function loadRooms(query = '') {
        try {
            loading.style.display = 'block';
            roomList.innerHTML = '';

            const params = new URLSearchParams();
            if (query) params.append('q', query);

            const response = await fetch(`/api/rooms/list?${params.toString()}`);
            if (!response.ok) throw new Error('Failed to fetch rooms');

            const data = await response.json();

            if (!data.success) {
                throw new Error(data.message || 'Failed to load rooms');
            }

            if (data.rooms.length === 0) {
                roomList.innerHTML = `
                    <div class="no-rooms">
                        <p>No rooms found${query ? ` matching "${query}"` : ''}.</p>
                        <a href="/rooms/create" class="btn btn-primary">Create a Room</a>
                    </div>
                `;
            } else {
                roomList.innerHTML = data.rooms.map(createRoomCard).join('');
            }
        } catch (error) {
            console.error('Error loading rooms:', error);
            roomList.innerHTML = '<div class="error-message">Failed to load rooms. Please try again.</div>';
        } finally {
            loading.style.display = 'none';
        }
    }

    // Event Listeners

    searchInput?.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => loadRooms(e.target.value.trim()), 300);
    });

    searchBtn?.addEventListener('click', () => {
        loadRooms(searchInput.value.trim());
    });

    // Popup controls

    joinBtn?.addEventListener('click', () => {
        joinPopup.style.display = 'block';
        joinCodeInput.focus();
    });

    popupCancelBtn?.addEventListener('click', () => {
        joinPopup.style.display = 'none';
        joinCodeInput.value = '';
    });

    popupJoinBtn?.addEventListener('click', () => {
        const code = joinCodeInput.value.trim();
        if (code) {
            joinRoom(null, code);
            joinPopup.style.display = 'none';
            joinCodeInput.value = '';
        } else {
            alert('Please enter a room code')
        }
    });

    // Auto-uppercase join code input
    joinCodeInput?.addEventListener('input', () => {
        joinCodeInput.value = joinCodeInput.value.toUpperCase();
    });

    // Join room on 'Enter'
    joinCodeInput?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const code = joinCodeInput.value.trim();
            if (code) {
                joinRoom(null, code);
                joinPopup.style.display = 'none';
                joinCodeInput.value = '';
            }
        }
    });

    // Close popup if user clicks outside div
    window.addEventListener('click', (e) => {
        if (e.target === joinPopup) {
            joinPopup.style.display = 'none';
            joinCodeInput.value = '';
        }
    });

    // Make joinRoom available globally for room card buttons
    window.joinRoom = (roomID) => joinRoom(roomID, null);

    // Initial load
    loadRooms();
});