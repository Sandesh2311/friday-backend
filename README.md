# F.R.I.D.A.Y AI Virtual Assistant

**F.R.I.D.A.Y** (Female Real-time Intelligent Decisive Assistant System) is a browser-based AI virtual assistant modeled exactly on the internship report. It integrates voice/text command capture, database persistence, rule-based operations, widgets for reminders, weather, and news, and fallback AI responses.

---

## 🏗️ Architecture Layer Mapping

1. **Client Layer (Frontend UI):**
   - Translucent glassmorphic interface built using semantic HTML5, modern vanilla CSS, and vanilla JavaScript.
   - Live system status indicators (`Idle`, `Listening`, `Processing`).
   - Dynamic right-hand sidebar for weather feeds, headlines, and reminder list widgets.
   - Settings modal for volume, speech rate, theme toggle, and weather defaults.
   - Text to speech synthesis and speech recognition utilizing browser native APIs.
2. **Flask Application Layer (Backend APIs):**
   - Main entry point in `app.py` serving static files and exposing CRUD REST APIs for reminders, history log, settings, and chat processing.
   - Package layout in `backend/` containing modular handlers (`command_processor`, `models`, `db_setup`, `voice_module`, etc.).
3. **External Services Layer:**
   - OpenWeatherMap API for live local weather retrieval.
   - NewsAPI for latest top articles.
   - Google Gemini API (`gemini-2.5-flash`) via the official `google-genai` SDK for fallback assistant completions.
   - Pollinations AI for free, fast image generation.
4. **SQLite Data Layer:**
   - local SQLite database (`friday.db`) with tables: `users`, `reminders`, `interaction_log`, and `settings`.
   - Parameterized SQL CRUD operations.

---

## 🛠️ Features

- **Dual-Input Modality:** Submit commands by typing or speaking (utilizing native SpeechRecognition).
- **Phonetic Transliteration:** Automatically normalizes mixed Hindi/English speech text using `indic-transliteration`.
- **Command Categories:**
  - `open google` / `open youtube` / `open facebook` / `open linkedin`
  - `web search <query>` (launches Google search in new tab)
  - `play <song>` (checks local music library or redirects to YouTube query)
  - `weather` / `weather in <city>` (fetches live weather data)
  - `news` (scrapes top headlines)
  - `set reminder <action> at <time>` / `view reminders` (manages task persistence)
  - `view history` (fetches chat logs)
  - `generate image <description>` (renders visual creations using Pollinations AI)
  - General conversational questions (routed to Google Gemini API)
- **Settings Syncing:** Speech speed/volume, UI light/dark theme, and default cities persist across page reloads.

---

## 🚀 Setup & Execution

### 1. Installation

Clone/extract the repository, navigate to the folder, and install python dependencies:
```bash
pip install -r requirements.txt
```

### 2. Environment Variables

Copy `.env.example` to `.env` in the root folder:
```bash
cp .env.example .env
```
Fill in the credentials as desired:
- `GEMINI_API_KEY`: Required for fallback AI responses (using Google Gemini).
- `NEWS_API_KEY`: Required for live news feed (from newsapi.org).
- `WEATHER_API_KEY`: Required for live weather widget (from openweathermap.org).
- `SECRET_KEY`: Security token for web application session state.

*Note: If keys are missing, the application will activate graceful mock/simulated fallbacks without crashing.*

### 3. Run Locally

Start the Flask application server:
```bash
python app.py
```
Open a browser and navigate to:
```
http://127.0.0.1:5000/
```
The SQLite database `friday.db` will automatically initialize and seed default settings on the first startup.
