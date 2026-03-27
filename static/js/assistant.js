document.addEventListener("DOMContentLoaded", () => {
    const messageButton = document.getElementById('assistant');
    const messageContainer = document.getElementById('assistant-messages');
    const openMessages = document.getElementById('open-messages');
    const closeMessages = document.getElementById('close-messages');
    const STORAGE_KEY = "assistantChatState";
    const DEFAULT_INTRO = "Hi! I'm here to help. How can I assist you today?";
    let hasClosed = false;

    const submitButton = document.getElementById("send-message");
    const clearButton = document.getElementById("clear-chat");
    let messagesContent = document.getElementById("messages-content");
    let context = "You are an AI assistant embedded in a website to help users navigate and find information. Your responses should be concise and relevant to the user's queries about the website's content and features.";
    const ASSISTANT_ENDPOINT = "/api/assistant/";

    restoreChatState();

    console.log("AI script loaded", submitButton, messagesContent);

    clearButton.addEventListener('click', () => {
        removeChatState();
    })
    // add event listener to toggle message container
    messageButton.addEventListener('click', (e) => {
        if(messageContainer.classList.contains('messages-hide')) {
            messageContainer.classList.remove('messages-hide');
            messageContainer.classList.add('messages-show');
            messageButton.classList.add('assistant-close');
            openMessages.style.display = 'none';
            closeMessages.style.display = 'block';
            hasClosed = false;
        } else {
            messageContainer.classList.remove('messages-show');
            messageContainer.classList.add('messages-hide');
            messageButton.classList.remove('assistant-close');
            openMessages.style.display = 'block';
            closeMessages.style.display = 'none';
            hasClosed = true;
        }

        localStorage.setItem("assistantHasClosed", JSON.stringify(hasClosed));
    });

    submitButton.addEventListener("click", async (e) => {
        e.stopPropagation();
        console.log("Button clicked");
        await getMessage();
    });

    async function getMessage() {
        const userMessage = document.getElementById("user-message").value;
        console.log("User message:", userMessage);
        if (!userMessage.trim()) {
            console.log("Empty message");
            return;
        } else {
            appendMessage("user", userMessage);
            document.getElementById("user-message").value = "";
        }
        await sendMessage(userMessage);
    }

    async function sendMessage(message) {
        try {
            console.log("Sending message to Django assistant endpoint...");
            const csrfToken = getCsrfToken();
            const response = await fetch(ASSISTANT_ENDPOINT, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken
                },
                body: JSON.stringify({
                    context: context,
                    message: message
                })
            });
            
            console.log("Response status:", response.status);
            const rawResponse = await response.text();
            let data = {};
            try {
                data = rawResponse ? JSON.parse(rawResponse) : {};
            } catch (_parseError) {
                data = {};
            }
            console.log("API response:", data);
            
            if (!response.ok) {
                const errText = data.error || `Assistant request failed (${response.status}).`;
                getResponse(errText);
                return;
            }

            if (data.error) {
                console.error("API Error:", data.error);
                getResponse("API Error: " + data.error);
                return;
            }

            if (data.response) {
                getResponse(data.response, data);
            } else {
                console.log("Unexpected response structure:", JSON.stringify(data));
                getResponse("Sorry, I couldn't process that request.");
            }
        } catch (error) {
            console.error("Error:", error);
            getResponse("Sorry, there was an error: " + error.message);
        }
    }

    function getCsrfToken() {
        const tokenElement = document.querySelector('meta[name="csrf-token"]');
        return tokenElement ? tokenElement.getAttribute("content") || "" : "";
    }

    function getResponse(response, metadata = {}) {
        appendMessage("assistant", response, metadata);
    }

    function appendMessage(role, text, metadata = {}) {
        const newMessage = document.createElement("p");
        newMessage.className = role === "user" ? "sent-box" : "response-box";
        newMessage.textContent = text;
        messagesContent.appendChild(newMessage);
        if (
            role === "assistant"
            && metadata.show_navigation
            && typeof metadata.suggested_route === "string"
            && metadata.suggested_route.startsWith("/")
        ) {
            const buttonMessage = document.createElement("button")
            buttonMessage.className = "response-box button-navigation";
            buttonMessage.textContent = metadata.cta_label || "Navigation";
            buttonMessage.dataset.route = metadata.suggested_route;
            messagesContent.appendChild(buttonMessage);
        }
        saveChatState();
        scrollToBottom();
    }

    function saveChatState() {
        const chatState = Array.from(messagesContent.querySelectorAll("p.sent-box, p.response-box")).map((msg) => ({
            role: msg.classList.contains("sent-box") ? "user" : "assistant",
            text: (msg.textContent || "").trim()
        })).filter((msg) => msg.text !== "");

        const sanitizedState = sanitizeChatState(chatState);

        localStorage.setItem(STORAGE_KEY, JSON.stringify(sanitizedState));
        localStorage.setItem("assistantHasClosed", JSON.stringify(hasClosed));
    }
    function removeChatState(){
        localStorage.removeItem(STORAGE_KEY);
        localStorage.removeItem("assistantHasClosed");
        hasClosed = true;
        messagesContent.innerHTML = "";
        appendRestoredMessage("assistant", DEFAULT_INTRO);
        scrollToBottom();
    }

    function restoreChatState() {
        const saved = localStorage.getItem(STORAGE_KEY);
        const closedState = JSON.parse(localStorage.getItem("assistantHasClosed") || "true");
        if (!saved) {
            ensureSingleDefaultIntro();
            closeMessages.style.display = 'none';
            return;
        } else if (saved && closedState === false){
            messageContainer.classList.remove('messages-hide');
            messageContainer.classList.add('messages-show');
            messageButton.classList.add('assistant-close');
            openMessages.style.display = 'none';
            closeMessages.style.display = 'block';
        } else {
            messageContainer.classList.remove('messages-show');
            messageContainer.classList.add('messages-hide');
            messageButton.classList.remove('assistant-close');
            openMessages.style.display = 'block';
            closeMessages.style.display = 'none';
        }

        try {
            const chatState = sanitizeChatState(JSON.parse(saved));
            if (!Array.isArray(chatState)) {
                ensureSingleDefaultIntro();
                return;
            }

            messagesContent.innerHTML = "";

            if (chatState.length === 0) {
                appendRestoredMessage("assistant", DEFAULT_INTRO);
                scrollToBottom();
                return;
            }

            chatState.forEach((msg) => {
                if (!msg || typeof msg.text !== "string") {
                    return;
                }

                appendRestoredMessage(msg.role, msg.text);
            });

            scrollToBottom();
        } catch (error) {
            console.error("Failed to parse saved assistant chat state:", error);
            localStorage.removeItem(STORAGE_KEY);
            ensureSingleDefaultIntro();
        }
    }

    function appendRestoredMessage(role, text) {
        const restoredMessage = document.createElement("p");
        restoredMessage.className = role === "user" ? "sent-box" : "response-box";
        restoredMessage.textContent = text;
        messagesContent.appendChild(restoredMessage);
    }

    function sanitizeChatState(chatState) {
        if (!Array.isArray(chatState)) {
            return [];
        }

        let introSeen = false;

        return chatState.filter((msg) => {
            if (!msg || typeof msg.text !== "string") {
                return false;
            }

            const normalizedRole = msg.role === "user" ? "user" : "assistant";
            msg.role = normalizedRole;
            msg.text = msg.text.trim();

            if (msg.text === "") {
                return false;
            }

            const isDefaultIntro = msg.role === "assistant" && msg.text === DEFAULT_INTRO;
            if (isDefaultIntro) {
                if (introSeen) {
                    return false;
                }
                introSeen = true;
            }

            return true;
        });
    }

    function ensureSingleDefaultIntro() {
        const currentMessages = Array.from(messagesContent.querySelectorAll("p.sent-box, p.response-box")).map((msg) => ({
            role: msg.classList.contains("sent-box") ? "user" : "assistant",
            text: (msg.textContent || "").trim()
        }));

        const sanitizedMessages = sanitizeChatState(currentMessages);
        messagesContent.innerHTML = "";

        if (sanitizedMessages.length === 0) {
            appendRestoredMessage("assistant", DEFAULT_INTRO);
            return;
        }

        sanitizedMessages.forEach((msg) => appendRestoredMessage(msg.role, msg.text));
    }

    function scrollToBottom() {
        const messagesBody = document.getElementById('messages-body');
        messagesBody.scrollTop = messagesBody.scrollHeight;
    }

    // Handle navigation buttons added dynamically in assistant replies.
    messagesContent.addEventListener("click", (e) => {
        const navigationButton = e.target.closest(".button-navigation");
        if (!navigationButton) {
            return;
        }

        const route = navigationButton.dataset.route || "";
        const allowedRoutes = new Set(["/about/", "/contact/", "/orders/", "/reviews/", "/account/login/", "/user-account/"]);
        if (!allowedRoutes.has(route)) {
            return;
        }

        e.stopPropagation();
        window.location.href = route;
    });
});