document.addEventListener('DOMContentLoaded', () => {
    const chatWindow = document.getElementById('chat-window');
    const userNameInput = document.getElementById('user-name');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    let userName = localStorage.getItem('userName');

    if (!userName) {
        userName = prompt('Please enter your name:');
        if (userName) {
            localStorage.setItem('userName', userName);
            userNameInput.value = userName;
        }
    } else {
        userNameInput.value = userName;
    }

    // Load chat history
    if (userName) {
        fetch(`/history?user_name=${encodeURIComponent(userName)}`)
            .then(response => response.json())
            .then(data => {
                data.forEach(log => {
                    const msgDiv = document.createElement('div');
                    msgDiv.textContent = `${log.role === 'user' ? userName : 'Megha'}: ${log.message}`;
                    msgDiv.className = log.role === 'user' ? 'chat-user' : 'chat-megha';
                    chatWindow.appendChild(msgDiv);
                });
                chatWindow.scrollTop = chatWindow.scrollHeight;
            })
            .catch(error => console.error('Error loading history:', error));
    }

    sendButton.addEventListener('click', async () => {
        const userName = userNameInput.value.trim();
        const message = messageInput.value.trim();
        if (userName && message) {
            const userMsg = document.createElement('div');
            userMsg.textContent = `${userName}: ${message}`;
            userMsg.className = 'chat-user';
            chatWindow.appendChild(userMsg);
            chatWindow.scrollTop = chatWindow.scrollHeight;

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_name: userName, message })
                });
                const data = await response.json();
                if (data.error) {
                    console.error('Error:', data.error);
                    return;
                }
                const meghaMsg = document.createElement('div');
                meghaMsg.textContent = `Megha: ${data.response}`;
                meghaMsg.className = 'chat-megha';
                chat