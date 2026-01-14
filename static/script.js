document.addEventListener('DOMContentLoaded', () => {
    const settingsModal = document.getElementById('settings-modal');
    const apiKeyInput = document.getElementById('api-key-input');
    const saveKeyBtn = document.getElementById('save-key-btn');
    const paramsBtn = document.getElementById('params-btn');
    const chatHistory = document.getElementById('chat-history');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');

    let apiKey = localStorage.getItem('openai_api_key');

    // --- State Management ---
    if (!apiKey) {
        settingsModal.classList.add('active');
    }

    saveKeyBtn.addEventListener('click', () => {
        const key = apiKeyInput.value.trim();
        if (key) {
            apiKey = key;
            localStorage.setItem('openai_api_key', key);
            settingsModal.classList.remove('active');
            addMessage('system', 'API Key saved! You can now start chatting.');
        } else {
            alert('Please enter a valid API Key.');
        }
    });

    paramsBtn.addEventListener('click', () => {
        apiKeyInput.value = apiKey || '';
        settingsModal.classList.add('active');
    });

    // Close modal when clicking outside content
    settingsModal.addEventListener('click', (e) => {
        if (e.target === settingsModal && apiKey) {
            settingsModal.classList.remove('active');
        }
    });

    // --- Chat Logic ---
    async function sendMessage() {
        const text = userInput.value.trim();
        if (!text) return;

        if (!apiKey) {
            settingsModal.classList.add('active');
            return;
        }

        // Add user message
        addMessage('user', text);
        userInput.value = '';
        userInput.style.height = 'auto'; // Reset height

        // Show loading state (optional, or just wait)
        const loadingId = addMessage('bot', 'Thinking... 🎵');

        try {
            const response = await fetch('https://api.openai.com/v1/chat/completions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${apiKey}`
                },
                body: JSON.stringify({
                    model: "gpt-4o", // Using a widely available model
                    messages: [
                        {
                            role: "system",
                            content: `You are a helpful assistant that answers clearly.
                                      You are specialized in music and you can answer to every question about music.
                                      Avoid unnecessary jargon.
                                      The users can sing songs, write lyrics, etc and you will be able to play the continuing of the song.`
                        },
                        { role: "user", content: text }
                    ]
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error?.message || 'API Error');
            }

            const data = await response.json();
            const aiText = data.choices[0].message.content;

            // Update loading message with actual response
            updateMessage(loadingId, aiText);

        } catch (error) {
            updateMessage(loadingId, `Error: ${error.message}. Please check your API Key in settings.`);
            console.error(error);
        }
    }

    // --- UI Helpers ---
    function addMessage(role, text) {
        const msgDiv = document.createElement('div');
        msgDiv.classList.add('message', role);
        const id = Date.now().toString(); // unique ID
        msgDiv.dataset.id = id;

        const contentDiv = document.createElement('div');
        contentDiv.classList.add('message-content');
        
        // Simple markdown parsing for bold/italic could be added here if needed
        // For now, we'll just set textContent to avoid XSS, but let's allow basic newlines
        contentDiv.innerText = text; 

        msgDiv.appendChild(contentDiv);
        chatHistory.appendChild(msgDiv);
        scrollToBottom();
        return id;
    }

    function updateMessage(id, newText) {
        const msgDiv = chatHistory.querySelector(`.message[data-id="${id}"]`);
        if (msgDiv) {
            const contentDiv = msgDiv.querySelector('.message-content');
            contentDiv.innerText = newText;
            scrollToBottom();
        }
    }

    function scrollToBottom() {
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    // --- Event Listeners ---
    sendBtn.addEventListener('click', sendMessage);

    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Auto-resize textarea
    userInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
        if(this.value === '') this.style.height = '50px';
    });
});
