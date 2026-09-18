document.addEventListener('DOMContentLoaded', function () {
    const chatBubble = document.getElementById('chat-bubble');
    const chatWindow = document.getElementById('chat-window');
    const closeChatBtn = document.getElementById('close-chat');
    const sendBtn = document.getElementById('send-btn');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');

    if (!chatBubble || !chatWindow) return;

    // UI Elements for Maximize/Resize
    const headerActions = document.querySelector('.chat-header-actions');

    // Add Maximize Button
    const maxBtn = document.createElement('button');
    maxBtn.innerHTML = '<i class="bi bi-arrows-fullscreen"></i>';
    maxBtn.className = 'btn-chat-action';
    maxBtn.title = 'Maximize / Restore Chat';
    maxBtn.setAttribute('aria-label', 'Maximize Chat Window');

    if (headerActions) {
        headerActions.insertBefore(maxBtn, closeChatBtn);
    }

    // Chat History Management
    let chatHistory = [];

    // Toggle Chat Window
    chatBubble.addEventListener('click', function () {
        chatWindow.classList.toggle('d-none');
        if (!chatWindow.classList.contains('d-none')) {
            chatInput.focus();
            scrollToBottom();
        }
    });

    if (closeChatBtn) {
        closeChatBtn.addEventListener('click', function () {
            chatWindow.classList.add('d-none');
        });
    }

    // Maximize/Restore Toggle
    maxBtn.addEventListener('click', function () {
        chatWindow.classList.toggle('maximized');
        const icon = maxBtn.querySelector('i');
        if (chatWindow.classList.contains('maximized')) {
            icon.classList.remove('bi-arrows-fullscreen');
            icon.classList.add('bi-fullscreen-exit');
        } else {
            icon.classList.remove('bi-fullscreen-exit');
            icon.classList.add('bi-arrows-fullscreen');
        }
    });

    // Send Message Event Listeners
    if (sendBtn) {
        sendBtn.addEventListener('click', sendMessage);
    }
    if (chatInput) {
        chatInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }

    function sendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;

        // Add User Message
        addMessage(message, 'user');
        chatInput.value = '';

        // Update History
        chatHistory.push({ role: 'user', parts: [message] });

        // Show Loading Indicator
        const loadingId = addLoading();

        // Call API
        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                history: chatHistory
            }),
        })
            .then(response => response.json())
            .then(data => {
                removeLoading(loadingId);
                const responseText = data.response || "No response received.";

                // Update History with Model Response
                chatHistory.push({ role: 'model', parts: [responseText] });

                // Format Markdown simple
                const formatted = formatMessage(responseText);
                addMessage(formatted, 'bot', true);
            })
            .catch(error => {
                removeLoading(loadingId);
                addMessage('Encountered an issue connecting to the counseling service. Please try again.', 'bot');
                console.error('Chat Error:', error);
            });
    }

    function addMessage(text, sender, isHtml = false) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${sender}-message`);

        const contentDiv = document.createElement('div');
        contentDiv.classList.add('message-content');

        if (isHtml) {
            contentDiv.innerHTML = text;
        } else {
            contentDiv.textContent = text;
        }

        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);
        scrollToBottom();
        return messageDiv;
    }

    function addLoading() {
        const id = 'loading-' + Date.now();
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', 'bot-message', 'loading-msg');
        messageDiv.id = id;

        const contentDiv = document.createElement('div');
        contentDiv.classList.add('message-content');
        contentDiv.innerHTML = '<div class="typing-indicator"><span></span><span></span><span></span></div>';

        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);
        scrollToBottom();
        return id;
    }

    function removeLoading(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function formatMessage(text) {
        // Safe Markdown formatter
        let formatted = text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            .replace(/\n\s*-\s/g, '<br>• ')
            .replace(/\n/g, '<br>');
        return formatted;
    }
});
