// Flask Messages (Flash)
document.addEventListener('DOMContentLoaded', () => {
    const flashMessages = document.querySelectorAll('.flash-message');

    flashMessages.forEach(message => {
        // Add close button
        const closeBtn = document.createElement('button')
        closeBtn.innerHTML = 'x';
        closeBtn.className = 'close-message';
        closeBtn.onclick = () => {
            message.style.opacity = '0';
            setTimout(() => {
                message.remove();
            }, 300); // Wait for fade out animation
        };
        message.appendChild(closeBtn);

        // Automatically close message after 5 seconds
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                message.remove();
            }, 300); // Wait for fade out animation
        }, 5000);
    });
});

// JavaScript Event Notifications
function jsMessage(message, type = 'info') {
    const container = document.querySelector('.js-messages');
    if (!container) return;

    const notification = document.createElement('div');
    notification.className = `js-message ${type}`;
    notification.innerHTML = message;

    // Add close button
    const closeBtn = document.createElement('button');
    closeBtn.innerHTML = 'x';
    closeBtn.className = 'close-message';
    closeBtn.onlcick = () => {
        notification.style.opacity = '0';
        setTimout(() => notification.remove(), 300); // Wait for fade out animation
    };
    notification.appendChild(closeBtn);

    container.appendChild(notification);

    // Automatically close message after 5 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);// Wait for fade out animation
    }, 5000);
}

// Export Utilities
window.appUtils = {
    jsMessage
};