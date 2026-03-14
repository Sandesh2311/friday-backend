async function sayHello() {
    const msgInput = document.getElementById("msg");
    const chatBox = document.getElementById("chat-box");
    const msg = msgInput.value.trim();

    if (!msg) return;

    const userDiv = document.createElement("div");
    userDiv.className = "message user";
    userDiv.innerText = msg;
    chatBox.appendChild(userDiv);
    msgInput.value = "";

    const botDiv = document.createElement("div");
    botDiv.className = "message bot";
    botDiv.innerHTML = '<div class="loader"></div>';
    chatBox.appendChild(botDiv);
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        const res = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: msg })
        });

        const data = await res.json();

        if (!res.ok) {
            botDiv.innerText = data.data || "Request failed";
            return;
        }

        if (data.type === "text") {
            botDiv.innerText = data.data;
            speak(data.data);
        } else if (data.type === "action") {
            window.open(data.data, "_blank", "noopener,noreferrer");
            botDiv.innerText = "Opening for you";
            speak("Opening for you");
        } else if (data.type === "image") {
            const img = document.createElement("img");
            img.src = data.data;
            img.alt = "Generated image";

            botDiv.innerHTML = "";
            botDiv.appendChild(img);
        } else {
            botDiv.innerText = "Unexpected response from Friday";
        }
    } catch (err) {
        botDiv.innerText = "Error connecting to Friday";
    }

    chatBox.scrollTop = chatBox.scrollHeight;
}

function startListening() {
    if (!("webkitSpeechRecognition" in window)) {
        alert("Voice recognition is supported in Chrome and Edge.");
        return;
    }

    const recognition = new webkitSpeechRecognition();
    recognition.lang = "en-IN";
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => {
        document.getElementById("msg").placeholder = "Listening...";
    };

    recognition.onresult = (event) => {
        const text = event.results[0][0].transcript;
        document.getElementById("msg").value = text;
        sayHello();
    };

    recognition.onerror = () => {
        document.getElementById("msg").placeholder = "Type your message...";
    };

    recognition.onend = () => {
        document.getElementById("msg").placeholder = "Type your message...";
    };

    recognition.start();
}

function speak(text) {
    if (!("speechSynthesis" in window)) return;

    const utterance = new SpeechSynthesisUtterance(text);
    const isHindi = /[\u0900-\u097F]/.test(text);
    utterance.lang = isHindi ? "hi-IN" : "en-IN";

    const voices = speechSynthesis.getVoices();
    for (const voice of voices) {
        if (
            (isHindi && voice.lang === "hi-IN") ||
            (!isHindi && voice.lang === "en-IN" && voice.name.toLowerCase().includes("female"))
        ) {
            utterance.voice = voice;
            break;
        }
    }

    utterance.rate = 1;
    utterance.pitch = 1;

    speechSynthesis.cancel();
    speechSynthesis.speak(utterance);
}
