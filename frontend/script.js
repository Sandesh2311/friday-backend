
async function sayHello() {
    const msgInput = document.getElementById("msg");
    const chatBox = document.getElementById("chat-box");
    const msg = msgInput.value.trim();
    if (!msg) return;

    // User message
    const userDiv = document.createElement("div");
    userDiv.className = "message user";
    userDiv.innerText = msg;
    chatBox.appendChild(userDiv);
    msgInput.value = "";

    // Loader
    const botDiv = document.createElement("div");
    botDiv.className = "message bot";
    botDiv.innerHTML = `<div class="loader"></div>`;
    chatBox.appendChild(botDiv);
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        const res = await fetch("https://YOUR_BACKEND_URL/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: msg })
        });

        const data = await res.json();
        // botDiv.innerHTML = "";

        // 🔥 TEXT RESPONSE
        if (data.type === "text") {
    botDiv.innerText = data.data;
    speak(data.data);   // 🔊 Friday बोलेगी
}
 else if (data.type === "action") {
    window.open(data.data, "_blank");
    botDiv.innerText = "Opening for you 🚀";
    speak("Opening for you");
}


     else if (data.type === "image") {
    const img = document.createElement("img");
    img.src = data.data + "?t=" + Date.now(); // cache bypass
    img.style.maxWidth = "100%";
    img.style.borderRadius = "10px";

    botDiv.innerHTML = "";
    botDiv.appendChild(img);

    chatBox.scrollTop = chatBox.scrollHeight;
    return;
}



        

    } catch (err) {
        botDiv.innerText = "Error connecting to Friday 😕";
    }

    chatBox.scrollTop = chatBox.scrollHeight;
}
function startListening() {
    if (!('webkitSpeechRecognition' in window)) {
        alert("Voice recognition not supported. Use Chrome or Edge.");
        return;
    }

    const recognition = new webkitSpeechRecognition();
    recognition.lang = "en-IN"; // Hindi + English
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => {
        document.getElementById("msg").placeholder = "Listening...";
    };

    recognition.onresult = (event) => {
        const text = event.results[0][0].transcript;
        document.getElementById("msg").value = text;
        sayHello(); // auto send
    };

    recognition.onerror = (event) => {
        console.error("Mic error:", event);
        document.getElementById("msg").placeholder = "Type your message...";
    };

    recognition.onend = () => {
        document.getElementById("msg").placeholder = "Type your message...";
    };

    recognition.start();
}
function speak(text) {
    if (!('speechSynthesis' in window)) return;

    const utterance = new SpeechSynthesisUtterance(text);

    // Language detect (simple)
    const isHindi = /[\u0900-\u097F]/.test(text);
    utterance.lang = isHindi ? "hi-IN" : "en-IN";

    // Female voice try
    const voices = speechSynthesis.getVoices();
    for (let v of voices) {
        if (
            (isHindi && v.lang === "hi-IN") ||
            (!isHindi && v.lang === "en-IN" && v.name.toLowerCase().includes("female"))
        ) {
            utterance.voice = v;
            break;
        }
    }

    utterance.rate = 1;
    utterance.pitch = 1;

    speechSynthesis.cancel(); // stop previous
    speechSynthesis.speak(utterance);
}
