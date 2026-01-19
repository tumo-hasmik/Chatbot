//UPDATED VERSION


document.addEventListener('DOMContentLoaded', () => {
    const chatHistory = document.getElementById('chat-history');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');

    async function sendMessage() {
        const text = userInput.value.trim();
        if (!text) return;

        // Add user message
        addMessage('user', text);
        userInput.value = '';
        userInput.style.height = 'auto';

        // Show loading
        const loadingId = addMessage('bot', 'Thinking... 🎵');

        try {
            // Call your Flask backend
            const response = await fetch('http://127.0.0.1:5000/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: text })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `Server Error: ${response.status}`);
            }

            const data = await response.json();
            const aiText = data.response;

            updateMessage(loadingId, aiText);

        } catch (error) {
            updateMessage(loadingId, `Error: ${error.message}. Make sure the backend is running!`);
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
    userInput.addEventListener('input', function () {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
        if (this.value === '') this.style.height = '50px';
    });
});



// document.addEventListener('DOMContentLoaded', () => {
//     const chatHistory = document.getElementById('chat-history');
//     const userInput = document.getElementById('user-input');
//     const sendBtn = document.getElementById('send-btn');

    

//     async function sendMessage() {
//         const text = userInput.value.trim();
//         if (!text) return;

//         // Add user message
//         addMessage('user', text);
//         userInput.value = '';
//         userInput.style.height = 'auto';

//         // Show loading
//         const loadingId = addMessage('bot', 'Thinking... 🎵');

//         try {
//             // Call your backend instead of OpenAI directly
//             const response = await fetch('http://127.0.0.1:5000/chat', {
//                 method: 'POST',
//                 headers: { 'Content-Type': 'application/json' },
//                 body: JSON.stringify({ prompt: text })
//             });

//             if (!response.ok) {
//                 const errorData = await response.json().catch(() => ({}));
//                 throw new Error(errorData.error || `Server Error: ${response.status}`);
//             }

//             const data = await response.json();
//             const aiText = data.response;

//             updateMessage(loadingId, aiText);

//         } catch (error) {
//             updateMessage(loadingId, `Error: ${error.message}. Is the backend running?`);
//             console.error(error);
//         }
//     }

//     // --- UI Helpers ---
//     function addMessage(role, text) {
//         const msgDiv = document.createElement('div');
//         msgDiv.classList.add('message', role);
//         const id = Date.now().toString(); // unique ID
//         msgDiv.dataset.id = id;

//         const contentDiv = document.createElement('div');
//         contentDiv.classList.add('message-content');

//         contentDiv.innerText = text;

//         msgDiv.appendChild(contentDiv);
//         chatHistory.appendChild(msgDiv);
//         scrollToBottom();
//         return id;
//     }

//     function updateMessage(id, newText) {
//         const msgDiv = chatHistory.querySelector(`.message[data-id="${id}"]`);
//         if (msgDiv) {
//             const contentDiv = msgDiv.querySelector('.message-content');
//             contentDiv.innerText = newText;
//             scrollToBottom();
//         }
//     }

//     function scrollToBottom() {
//         chatHistory.scrollTop = chatHistory.scrollHeight;
//     }

//     // --- Event Listeners ---
//     sendBtn.addEventListener('click', sendMessage);

//     userInput.addEventListener('keydown', (e) => {
//         if (e.key === 'Enter' && !e.shiftKey) {
//             e.preventDefault();
//             sendMessage();
//         }
//     });

//     // Auto-resize textarea
//     userInput.addEventListener('input', function () {
//         this.style.height = 'auto';
//         this.style.height = (this.scrollHeight) + 'px';
//         if (this.value === '') this.style.height = '50px';
//     });
// });
