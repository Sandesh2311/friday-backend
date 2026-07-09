// Global settings state
let systemSettings = {
    theme: "dark",
    voice_enabled: 1,
    volume: 1.0,
    rate: 190,
    weather_city: "Mumbai"
};

// Web Speech Recognition instance
let recognition = null;
let isListening = false;

// Initialize on page load
window.addEventListener("DOMContentLoaded", () => {
    initApp();
});

async function initApp() {
    await fetchSettings();
    await fetchReminders();
    
    // Lazy fetch weather and news updates on startup
    fetchWeatherWidget();
    fetchNewsWidget();
}

/* ==========================================================================
   REST API INTEGRATION (SETTINGS, REMINDERS, HISTORY)
   ========================================================================== */

// Fetch settings from server
async function fetchSettings() {
    try {
        const res = await fetch("/api/settings");
        if (res.ok) {
            systemSettings = await res.json();
            applySettingsUI();
        }
    } catch (err) {
        console.error("Error loading settings:", err);
    }
}

// Apply settings state to UI controls and document body
function applySettingsUI() {
    // Theme
    if (systemSettings.theme === "light") {
        document.body.classList.remove("dark-theme");
        document.body.classList.add("light-theme");
    } else {
        document.body.classList.remove("light-theme");
        document.body.classList.add("dark-theme");
    }
    
    // Modal controls
    document.getElementById("setting-theme").value = systemSettings.theme;
    document.getElementById("setting-voice").checked = systemSettings.voice_enabled === 1;
    document.getElementById("setting-volume").value = systemSettings.volume;
    document.getElementById("setting-rate").value = systemSettings.rate;
    document.getElementById("setting-weather-city").value = systemSettings.weather_city;
}

// Save settings to server
async function saveSettings() {
    systemSettings.theme = document.getElementById("setting-theme").value;
    systemSettings.voice_enabled = document.getElementById("setting-voice").checked ? 1 : 0;
    systemSettings.volume = parseFloat(document.getElementById("setting-volume").value);
    systemSettings.rate = parseInt(document.getElementById("setting-rate").value);
    systemSettings.weather_city = document.getElementById("setting-weather-city").value.trim() || "Mumbai";
    
    try {
        const res = await fetch("/api/settings", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(systemSettings)
        });
        if (res.ok) {
            const updated = await res.json();
            systemSettings = updated;
            applySettingsUI();
            
            // Auto refresh weather widget in case default city changed
            fetchWeatherWidget();
        }
    } catch (err) {
        console.error("Error saving settings:", err);
    }
}

// Fetch reminders from database
async function fetchReminders() {
    try {
        const res = await fetch("/api/reminders");
        if (res.ok) {
            const reminders = await res.json();
            const list = document.getElementById("reminders-list");
            const emptyState = document.getElementById("reminder-empty-state");
            const countBadge = document.getElementById("reminder-count");
            list.innerHTML = "";

            const activeReminders = reminders.filter(r => r.status !== "completed");
            countBadge.textContent = `${activeReminders.length} pending`;

            if (activeReminders.length === 0) {
                emptyState.style.display = "flex";
                list.style.display = "none";
                return;
            }

            emptyState.style.display = "none";
            list.style.display = "flex";

            activeReminders.forEach(r => {
                const li = document.createElement("li");
                li.className = `reminder-item ${r.status === 'completed' ? 'completed' : ''}`;

                const dateLabel = r.date ? new Date(`${r.date}T${r.time || '00:00'}`).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }) : "Today";
                const timeLabel = r.time ? r.time : "Any time";
                const priorityClass = r.priority || "medium";

                li.innerHTML = `
                    <div class="reminder-main">
                        <div class="reminder-topline">
                            <span class="reminder-title">${r.text}</span>
                            <span class="priority-pill ${priorityClass}">${priorityClass}</span>
                        </div>
                        <div class="reminder-meta">
                            <span>🗓 ${dateLabel}</span>
                            <span>⏰ ${timeLabel}</span>
                        </div>
                    </div>
                    <div class="reminder-actions">
                        <button class="rem-btn complete" onclick="completeReminder(${r.id})" title="Mark completed">✓</button>
                        <button class="rem-btn delete" onclick="deleteReminder(${r.id})" title="Delete">✕</button>
                    </div>
                `;
                list.appendChild(li);
            });
        }
    } catch (err) {
        console.error("Error fetching reminders:", err);
    }
}

function openReminderModal() {
    document.getElementById("reminder-text-input").value = "";
    document.getElementById("reminder-date-input").value = "";
    document.getElementById("reminder-time-input").value = "";
    document.getElementById("reminder-priority-input").value = "medium";
    openModal("reminder-modal");
}

async function submitReminderForm() {
    const text = document.getElementById("reminder-text-input").value.trim();
    const date = document.getElementById("reminder-date-input").value;
    const time = document.getElementById("reminder-time-input").value;
    const priority = document.getElementById("reminder-priority-input").value;

    if (!text || !time) {
        alert("Please enter both a reminder description and time.");
        return;
    }

    try {
        const res = await fetch("/api/reminders", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text, time, date, priority })
        });

        if (res.ok) {
            closeModal("reminder-modal");
            await fetchReminders();
            speak("Reminder saved successfully");
        }
    } catch (err) {
        console.error("Error adding reminder:", err);
    }
}

// Complete reminder
async function completeReminder(id) {
    try {
        const res = await fetch("/api/reminders/complete", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ id })
        });
        if (res.ok) {
            fetchReminders();
        }
    } catch (err) {
        console.error("Error completing reminder:", err);
    }
}

// Delete reminder
async function deleteReminder(id) {
    try {
        const res = await fetch(`/api/reminders/${id}`, {
            method: "DELETE"
        });
        if (res.ok) {
            fetchReminders();
        }
    } catch (err) {
        console.error("Error deleting reminder:", err);
    }
}

setInterval(() => {
    fetchReminders();
}, 20000);

// Clear interaction logs
async function clearChatHistory() {
    if (!confirm("Are you sure you want to clear all chat interaction logs?")) return;
    try {
        const res = await fetch("/api/history", {
            method: "DELETE"
        });
        if (res.ok) {
            document.getElementById("chat-box").innerHTML = "";
            appendMessage("bot", "Chat history logs cleared.");
            closeModal("settings-modal");
        }
    } catch (err) {
        console.error("Error clearing logs:", err);
    }
}

/* ==========================================================================
   SIDEBAR WIDGET FEEDS (WEATHER & NEWS)
   ========================================================================== */

async function fetchWeatherWidget() {
    const infoText = document.getElementById("weather-info");
    const city = systemSettings.weather_city || "Mumbai";
    try {
        // Run simulated or actual weather backend trigger
        const res = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: `weather in ${city}` })
        });
        if (res.ok) {
            const data = await res.json();
            infoText.innerText = data.data;
        } else {
            infoText.innerText = "Weather unavailable.";
        }
    } catch (err) {
        infoText.innerText = "Weather unavailable.";
    }
}

async function updateWeatherCity() {
    const input = document.getElementById("weather-city-input");
    const city = input.value.trim();
    if (!city) return;
    
    // Save to settings
    document.getElementById("setting-weather-city").value = city;
    await saveSettings();
    input.value = "";
}

async function fetchNewsWidget() {
    const newsBox = document.getElementById("news-info");
    try {
        const res = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: "news" })
        });
        if (res.ok) {
            const data = await res.json();
            // Split headlines into paragraph elements
            const headlines = data.data.split(" | ");
            newsBox.innerHTML = headlines.map(h => `<p style="margin-bottom: 8px; border-bottom: 1px solid var(--panel-border); padding-bottom: 4px;">📌 ${h}</p>`).join("");
        } else {
            newsBox.innerText = "News headlines unavailable.";
        }
    } catch (err) {
        newsBox.innerText = "News headlines unavailable.";
    }
}

/* ==========================================================================
   CHAT MESSAGING FLOW
   ========================================================================== */

// Event listener for Enter key
document.getElementById("msg").addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
        sendMessage();
    }
});

// Main Send Message flow
async function sendMessage() {
    const input = document.getElementById("msg");
    const text = input.value.trim();
    if (!text) return;
    
    input.value = "";
    appendMessage("user", text);
    
    // Show bot thinking bubble
    const loaderId = appendLoader();
    setSystemStatus("processing", "System: Processing");
    
    try {
        const res = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: text })
        });
        
        removeLoader(loaderId);
        setSystemStatus("idle", "System: Idle");
        
        if (res.ok) {
            const responseData = await res.json();
            handleBotResponse(responseData);
            
            // Check if the command modifies database elements, if so, trigger refreshes
            const lowerText = text.toLowerCase();
            if (lowerText.includes("reminder") || lowerText.includes("remind")) {
                fetchReminders();
            }
            if (lowerText.includes("weather") || lowerText.includes("mausam")) {
                fetchWeatherWidget();
            }
            if (lowerText.includes("news") || lowerText.includes("khabar") || lowerText.includes("samachar")) {
                fetchNewsWidget();
            }
        } else {
            appendMessage("bot", "Sorry, I encountered a communication error with the server.");
        }
    } catch (err) {
        removeLoader(loaderId);
        setSystemStatus("idle", "System: Idle");
        appendMessage("bot", "Sorry, I couldn't reach the server. Make sure it is running.");
    }
}

// Render message bubble
function appendMessage(sender, text) {
    const chatBox = document.getElementById("chat-box");
    const div = document.createElement("div");
    div.className = `message ${sender}`;
    div.innerText = text;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Render bot loading bubble
function appendLoader() {
    const chatBox = document.getElementById("chat-box");
    const div = document.createElement("div");
    const loaderId = "loader-" + Date.now();
    div.id = loaderId;
    div.className = "message bot";
    div.innerHTML = `
        <span class="loader"></span>
        <span class="loader"></span>
        <span class="loader"></span>
    `;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
    return loaderId;
}

function removeLoader(id) {
    const loaderElement = document.getElementById(id);
    if (loaderElement) {
        loaderElement.remove();
    }
}

// Route JSON response type accordingly
function handleBotResponse(response) {
    const chatBox = document.getElementById("chat-box");
    const div = document.createElement("div");
    div.className = "message bot";
    
    if (response.type === "text") {
        div.innerText = response.data;
        chatBox.appendChild(div);
        speak(response.data);
    } else if (response.type === "action") {
        div.innerHTML = `Opening target link: <a href="${response.data}" target="_blank" style="color: var(--cyan-neon); text-decoration: underline;">${response.data}</a> 🚀`;
        chatBox.appendChild(div);
        speak("Opening website for you");
        window.open(response.data, "_blank");
    } else if (response.type === "image") {
        const img = document.createElement("img");
        img.src = response.data;
        img.alt = "Generated Image";
        img.style.maxWidth = "100%";
        img.style.borderRadius = "12px";
        img.style.marginTop = "6px";
        
        div.innerHTML = `<strong>Image Generated:</strong><br>`;
        div.appendChild(img);
        chatBox.appendChild(div);
        speak("Here is your generated image");
    }
    
    chatBox.scrollTop = chatBox.scrollHeight;
}

/* ==========================================================================
   SPEECH SYNTHESIS (VOICE OUTPUT)
   ========================================================================= */

function speak(text) {
    if (!systemSettings.voice_enabled || !('speechSynthesis' in window)) return;
    
    // Stop any ongoing speech
    speechSynthesis.cancel();
    
    const utterance = new SpeechSynthesisUtterance(text);
    
    // Detect if text contains Hindi characters
    const isHindi = /[\u0900-\u097F]/.test(text);
    utterance.lang = isHindi ? "hi-IN" : "en-IN";
    
    // Adjust rate and volume
    utterance.volume = systemSettings.volume;
    
    // Mapping: slider 50-250 to speech rate 0.5-2.5
    utterance.rate = systemSettings.rate / 100;
    
    // Try to set a female assistant voice
    const voices = speechSynthesis.getVoices();
    for (let v of voices) {
        if (isHindi && v.lang === "hi-IN") {
            utterance.voice = v;
            break;
        } else if (!isHindi && v.lang.startsWith("en-") && v.name.toLowerCase().includes("female")) {
            utterance.voice = v;
            break;
        }
    }
    
    speechSynthesis.speak(utterance);
}

// Proactively run getVoices to pre-cache browser voices
if ('speechSynthesis' in window) {
    speechSynthesis.getVoices();
}

/* ==========================================================================
   SPEECH RECOGNITION (VOICE INPUT)
   ========================================================================== */

function toggleVoiceInput() {
    if (isListening) {
        stopListening();
    } else {
        startListening();
    }
}

function startListening() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        alert("Voice recognition is not supported by your browser. Please try Chrome or Edge.");
        return;
    }
    
    recognition = new SpeechRecognition();
    recognition.lang = "en-IN"; // Set English-Indian (supports Hindi mix)
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    
    recognition.onstart = () => {
        isListening = true;
        document.getElementById("btn-mic").classList.add("active");
        document.getElementById("msg").placeholder = "Listening...";
        setSystemStatus("listening", "System: Listening");
    };
    
    recognition.onresult = (event) => {
        const speechResult = event.results[0][0].transcript;
        document.getElementById("msg").value = speechResult;
        sendMessage();
    };
    
    recognition.onerror = (event) => {
        console.error("Speech Recognition Error:", event.error);
        stopListening();
    };
    
    recognition.onend = () => {
        stopListening();
    };
    
    recognition.start();
}

function stopListening() {
    isListening = false;
    document.getElementById("btn-mic").classList.remove("active");
    document.getElementById("msg").placeholder = "Type your command...";
    setSystemStatus("idle", "System: Idle");
    if (recognition) {
        recognition.abort();
        recognition = null;
    }
}

/* ==========================================================================
   STATUS INDICATOR STATE CONTROLLERS
   ========================================================================== */

function setSystemStatus(state, label) {
    const dot = document.getElementById("status-dot");
    const text = document.getElementById("status-text");
    
    dot.className = "pulse-dot " + state;
    text.innerText = label;
}

/* ==========================================================================
   MODALS MANAGEMENT
   ========================================================================== */

function openModal(id) {
    document.getElementById(id).classList.add("open");
}

function closeModal(id) {
    document.getElementById(id).classList.remove("open");
}

// Close modal when clicking background
window.addEventListener("click", (e) => {
    if (e.target.classList.contains("modal-overlay")) {
        e.target.classList.remove("open");
    }
});
