var socket = io();

document.getElementById('send-btn').addEventListener('click', function() {
    sendMessage();
});

document.getElementById('user-message').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

function sendMessage() {
    var userMessage = document.getElementById('user-message').value;
    if (userMessage.trim() === '') {
        return;
    }

    // Display user message in the chat box
    appendMessage('You', userMessage);

    // Emit the message to the server
    socket.emit('user_message', { message: userMessage });

    // Clear input field
    document.getElementById('user-message').value = '';
}

// Listen for chatbot replies
socket.on('chatbot_reply', function(data) {
    appendMessage('Chatbot', data.reply);
});

function appendMessage(sender, message) {
    var chatBox = document.getElementById('chat-box');
    var messageElement = document.createElement('div');
    messageElement.innerHTML = `<strong>${sender}:</strong> ${message}`;
    chatBox.appendChild(messageElement);

    // Scroll to the bottom of the chat box
    chatBox.scrollTop = chatBox.scrollHeight;
}
