document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const chatbotWidget = document.getElementById('chatbot-widget');
    const chatbotToggle = document.getElementById('chatbot-toggle');
    const chatbotMessages = document.getElementById('chatbot-messages');
    const chatbotInput = document.getElementById('chatbot-input');
    const chatbotSend = document.getElementById('chatbot-send');
    
    // Set up initial state - show a welcome message
    addBotMessage("👋 Hi there! I'm your AI assistant. Ask me anything about this website!");
    
    // Toggle chatbot open/closed
    chatbotToggle.addEventListener('click', function() {
        if (chatbotWidget.classList.contains('chatbot-collapsed')) {
            chatbotWidget.classList.remove('chatbot-collapsed');
            chatbotWidget.classList.add('chatbot-expanded');
        } else {
            chatbotWidget.classList.remove('chatbot-expanded');
            chatbotWidget.classList.add('chatbot-collapsed');
        }
    });
    
    // Handle send button click
    chatbotSend.addEventListener('click', handleUserMessage);
    
    // Handle Enter key press in input
    chatbotInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            handleUserMessage();
        }
    });
    
    // Process user message
    function handleUserMessage() {
        const userMessage = chatbotInput.value.trim();
        if (userMessage) {
            // Display user message
            addUserMessage(userMessage);
            chatbotInput.value = '';
            
            // Add loading indicator
            const loadingMsgId = addBotMessage("Thinking...");
            
            // Make API call to backend for RAG-based response
            fetchRagResponse(userMessage)
                .then(botResponse => {
                    // Remove loading message and add actual response
                    replaceMessage(loadingMsgId, botResponse);
                })
                .catch(error => {
                    console.error('Error:', error);
                    replaceMessage(loadingMsgId, "Sorry, I encountered an error. Please try again later.");
                });
        }
    }
    
    // Function to add user message to chat
    function addUserMessage(text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user-message';
        
        const messageText = document.createElement('div');
        messageText.textContent = text;
        
        const messageTime = document.createElement('div');
        messageTime.className = 'message-time';
        messageTime.textContent = getCurrentTime();
        
        messageDiv.appendChild(messageText);
        messageDiv.appendChild(messageTime);
        
        chatbotMessages.appendChild(messageDiv);
        scrollToBottom();
    }
    
    // Function to add bot message to chat and return message ID
    function addBotMessage(text) {
        const messageId = 'msg-' + Date.now();
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot-message';
        messageDiv.id = messageId;
        
        const messageText = document.createElement('div');
        messageText.textContent = text;
        
        const messageTime = document.createElement('div');
        messageTime.className = 'message-time';
        messageTime.textContent = getCurrentTime();
        
        messageDiv.appendChild(messageText);
        messageDiv.appendChild(messageTime);
        
        chatbotMessages.appendChild(messageDiv);
        scrollToBottom();
        
        return messageId;
    }
    
    // Function to replace a message with a new one
    function replaceMessage(messageId, newText) {
        const messageDiv = document.getElementById(messageId);
        if (messageDiv) {
            const messageText = messageDiv.querySelector('div:not(.message-time)');
            messageText.textContent = newText;
        }
    }
    
    // Function to get current time in HH:MM format
    function getCurrentTime() {
        const now = new Date();
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        return `${hours}:${minutes}`;
    }
    
    // Function to scroll chat to bottom
    function scrollToBottom() {
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }
    
    // Mock function to fetch RAG response from backend
    // In a real implementation, this would make an API call to your backend
    async function fetchRagResponse(query) {
        // Simulating network delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // This is where you would call your backend API
        // const response = await fetch('/api/rag', {
        //     method: 'POST',
        //     headers: {
        //         'Content-Type': 'application/json',
        //     },
        //     body: JSON.stringify({ query }),
        // });
        // const data = await response.json();
        // return data.answer;
        
        // For now, return mock responses based on query keywords
        const lowerQuery = query.toLowerCase();
        
        if (lowerQuery.includes('f1') || lowerQuery.includes('student') || lowerQuery.includes('visa')) {
            return "F1 visas are for international students. Be sure to maintain full-time enrollment, get authorization before working, and keep your I-20 valid. Check out our F1-Students page for more details!";
        } else if (lowerQuery.includes('contact') || lowerQuery.includes('reach') || lowerQuery.includes('email')) {
            return "You can contact us by email at info@ragchatbotdemo.com, by phone at +1 (555) 123-4567, or by filling out the form on our Contact page.";
        } else if (lowerQuery.includes('rag') || lowerQuery.includes('chatbot') || lowerQuery.includes('how do you work')) {
            return "I'm a RAG (Retrieval-Augmented Generation) chatbot. I search through the content of this website to find relevant information to answer your questions. This helps me provide accurate information specific to this site's content.";
        } else {
            return "I'm your helpful assistant for this website. I can answer questions about F1 student visas, our contact information, and how I work. Is there something specific you'd like to know?";
        }
    }
    
    // Show the chatbot initially after a short delay
    setTimeout(() => {
        chatbotWidget.classList.remove('chatbot-collapsed');
        chatbotWidget.classList.add('chatbot-expanded');
    }, 1000);
});