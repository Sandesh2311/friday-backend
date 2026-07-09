import os
import urllib.parse
import re
from backend.voice_module import hindi_to_english
from backend.search_module import parse_and_search
from backend.reminder_module import process_reminder_command
from backend.weather_module import get_weather
from backend.news_module import get_top_news
from backend.ai.ai_provider import generate_ai_response
from backend.models import Settings, InteractionLog, Reminder

# Curated music library
MUSIC_LIBRARY = {
    "perfect": "https://youtu.be/2Vv-BfVoq4g",
    "shape of you": "https://youtu.be/JGwWNGJdvx8",
    "shapeofyou": "https://youtu.be/JGwWNGJdvx8",
    "believer": "https://youtu.be/7wtfhZwyrcc",
    "thunder": "https://youtu.be/fKopy74weus",
    "skyfall": "https://youtu.be/DeumyOzKqgI",
    "kesariya": "https://youtu.be/BddP6PYo2gs",
    "tum hi ho": "https://youtu.be/Umqb9KENgmk",
    "tumhiho": "https://youtu.be/Umqb9KENgmk",
    "apna bana le": "https://youtu.be/ElZfdU54Cp8",
    "apnabanale": "https://youtu.be/ElZfdU54Cp8",
    "faded": "https://youtu.be/60ItHLz5WEA",
    "cheap thrills": "https://youtu.be/nYh-n7EOtMA",
    "cheapthrills": "https://youtu.be/nYh-n7EOtMA"
}

def process_command(command: str, user_id: int):
    """
    Main router for F.R.I.D.A.Y commands.
    Checks rules sequentially, updates settings if needed,
    and returns a structured dict: {"type": "text"|"action"|"image", "data": "..."}
    """
    c = command.lower().strip()
    
    # 1. Normalize Devanagari Hindi transliteration to phonetic English
    normalized_cmd = hindi_to_english(c)
    nc = normalized_cmd.lower().strip()

    # 2. Open Website Commands
    if "open google" in nc or "google kholo" in nc or "google khol" in nc:
        return {"type": "action", "data": "https://google.com"}
        
    if "open youtube" in nc or "youtube kholo" in nc or "youtube khol" in nc:
        return {"type": "action", "data": "https://youtube.com"}
        
    if "open facebook" in nc or "facebook kholo" in nc:
        return {"type": "action", "data": "https://facebook.com"}
        
    if "open linkedin" in nc or "linkedin kholo" in nc:
        return {"type": "action", "data": "https://linkedin.com"}

    # 3. Image Generation Command (Pollinations API)
    if "image" in nc and any(k in nc for k in ["generate", "create", "make", "draw", "bana"]):
        prompt = command
        for word in ["generate", "create", "make", "draw", "image", "picture", "bana", "do", "tasveer"]:
            prompt = re.sub(r'\b' + re.escape(word) + r'\b', '', prompt, flags=re.IGNORECASE)
        prompt = prompt.strip()
        if not prompt:
            return {"type": "text", "data": "Please specify what image you'd like me to generate."}
            
        import uuid
        seed = uuid.uuid4().hex[:8]
        encoded = urllib.parse.quote(prompt)
        image_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&seed={seed}"
        return {"type": "image", "data": image_url}

    # 4. Play Music / YouTube Search Command
    if nc.startswith("play") or any(k in nc for k in ["gaana", "chala", "song", "music", "bajao"]):
        # Extract query text
        query = command
        for word in ["play", "song", "music", "gaana", "chala", "chalao", "bajao", "chala do", "baja do"]:
            query = re.sub(r'\b' + re.escape(word) + r'\b', '', query, flags=re.IGNORECASE)
        query = query.strip()
        
        if not query:
            return {"type": "text", "data": "What song would you like me to play?"}
            
        # Search local library
        norm_query = query.lower().replace(" ", "")
        for key, url in MUSIC_LIBRARY.items():
            if key.replace(" ", "") in norm_query or norm_query in key.replace(" ", ""):
                return {"type": "action", "data": url}
                
        # Fallback: Redirect to YouTube Search
        encoded_query = urllib.parse.quote(query)
        return {
            "type": "action",
            "data": f"https://www.youtube.com/results?search_query={encoded_query}"
        }

    # 5. Weather Commands
    if "weather" in nc or "mausam" in nc:
        # Check if city is specified, e.g. "weather in Delhi" or "weather of Tokyo"
        city_match = re.search(r"(?:weather in|weather of|weather for|mausam)\s+([a-zA-Z\s]+)", command, re.IGNORECASE)
        if city_match:
            city = city_match.group(1).strip()
        else:
            # Fallback: Get weather_city from Settings
            settings = Settings.get_by_user(user_id)
            city = settings.get("weather_city", "Mumbai")
        return get_weather(city)

    # 6. News Commands
    if any(k in nc for k in ["news", "khabar", "samachar", "headlines"]):
        return get_top_news()

    # 7. Reminders Commands
    if any(k in nc for k in ["reminder", "remind"]):
        return process_reminder_command(command, user_id)

    # 8. Web Search Commands
    if nc.startswith("web search") or "search google for" in nc or "search on google" in nc or nc.startswith("search for"):
        return parse_and_search(command)

    # 9. History Commands
    if "history" in nc or "logs" in nc or "log" in nc:
        logs = InteractionLog.get_all(user_id, limit=5)
        if not logs:
            return {"type": "text", "data": "You don't have any saved interaction history."}
        history_lines = []
        for l in reversed(logs):
            history_lines.append(f"You: {l['command']} | Friday: {l['response'][:60]}...")
        return {"type": "text", "data": "Recent History:\n" + "\n".join(history_lines)}

    # 10. Default Fallback: AI response engine
    ai_data = generate_ai_response(command)
    return {"type": "text", "data": ai_data}
