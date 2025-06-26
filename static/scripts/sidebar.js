// Chat Elements
const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-message');
const sendBtn = document.getElementById('send-message');
// Member List Elements
const memberCount = document.getElementById('member-count');
const memberList = document.getElementById('member-list');

const initChat = () => {
    if (!window.SEEDLINGS?.ROOM_ID || !window.SEEDLINGS?.socket) {
        setTimeout(initChat, 100); // Check again in 100ms
        return;
    }

    const socket = window.SEEDLINGS.socket;
    const roomID = window.SEEDLINGS.ROOM_ID;

    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    sendBtn.addEventListener('click', sendMessage);

    // Send Chat Message
    function sendMessage() {
        const content = chatInput.value.trim();
        if (!content) return;

        socket.emit('chat', {
            room_id: roomID,
            message: content
        });
        chatInput.value = '';
    }

    // Socket Event Handlers

    // Chat Socket Handlers

    socket.on('chat', (data) => {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'chat-message';
        msgDiv.innerHTML = `
            <span class="chat-user">${data.user}:</span>
            <span class="chat-content">${data.message_content}</span>
            <span class="chat-timestamp">${new Date(data.timestamp).toLocaleString()}</span>
        `; // Display chat message in User's local time
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    });

    socket.on('status', (data) => {
        const statusDiv = document.createElement('div');
        statusDiv.className = 'chat-status';
        statusDiv.textContent = data.message;
        chatMessages.appendChild(statusDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    });

    // Member List Socket Handlers
    socket.on('member_update', (data) => {
        memberCount.textContent = data.count;
        memberList.innerHTML = data.members
            .map(member => `
                <div class="member" data-user-id="${member.id}">
                    <span class="member-name">
                        ${member.username}
                        ${member.is_owner ? '<span class="owner-icon" title="Room Owner">👑</span>' : ''}
                    </span>
                </div>
            `).join('');
    });
}

// Start Initialisation when DOM is ready
document.addEventListener('DOMContentLoaded', initChat);