import os
import webbrowser
import requests
import yt_dlp
from openai import OpenAI
from project1_2.image_generator import generate_image
from project1_2.musicLibrary import music

from indic_transliteration.sanscript import transliterate
from indic_transliteration import sanscript
import os
from dotenv import load_dotenv

load_dotenv()


import os

ai_client = OpenAI(
    base_url="https://api.sambanova.ai/v1",
    api_key=os.getenv("OPENAI_API_KEY")
)


def hindi_to_english(text):
    try:
        return transliterate(text, sanscript.DEVANAGARI, sanscript.ITRANS)
    except:
        return text




def friday_engine(command: str):
    c = command.lower()

    # 🖼 IMAGE GENERATION
    if "image" in c and any(k in c for k in ["generate", "create", "make", "draw", "bana"]):
        prompt = c
        for w in ["generate", "create", "make", "draw", "image", "picture", "bana"]:
            prompt = prompt.replace(w, "")
        prompt = prompt.strip()

        if not prompt:
            return {"type": "text", "data": "Please describe the image"}

        image_path = generate_image(prompt)
        image_name = os.path.basename(image_path)

        return {
            "type": "image",
            "data": f"http://127.0.0.1:5000/images/{image_name}"
        }

# 🎵 MUSIC
    if c.startswith("play") or "gaana" in c:
        words = c.split()

        # 1️⃣ Local library
        for w in words:
            w = hindi_to_english(w).lower()
            if w in music:
                return {
                    "type": "action",
                    "data": music[w]
                }

        # 2️⃣ YouTube FIRST VIDEO autoplay
        query = (
            c.replace("play", "")
            .replace("gaana", "")
            .replace("song", "")
            .strip()
        )

        try:
            ydl_opts = {
                "quiet": True,
                "no_warnings": True,
                "default_search": "ytsearch1",
                "skip_download": True
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(query, download=False)
                video_url = info["entries"][0]["webpage_url"]

            return {
                "type": "action",
                "data": video_url + "&autoplay=1"
            }

        except:
            return {
                "type": "action",
                "data": f"https://www.youtube.com/results?search_query={query}"
            }


    # 🌐 OPEN WEBSITES (STRICT MATCH)
    if "open google" in c or "google kholo" in c:
        return {"type": "action", "data": "https://google.com"}

    if "open youtube" in c or "youtube kholo" in c:
        return {"type": "action", "data": "https://youtube.com"}

    if "open facebook" in c:
        return {"type": "action", "data": "https://facebook.com"}

    if "open linkedin" in c:
        return {"type": "action", "data": "https://linkedin.com"}

    # 📰 NEWS
    # 📰 NEWS
    if "news" in c or "khabar" in c:
        try:
            r = requests.get(
                "https://newsapi.org/v2/everything",
                params={
                    "q": "india",
                    "language": "en",
                    "sortBy": "publishedAt",
                    "apiKey": os.getenv("NEWS_API_KEY")
                },
                timeout=10
            )

            data = r.json()

            if data.get("articles"):
                headlines = [a["title"] for a in data["articles"][:5]]
                return {
                    "type": "text",
                    "data": " | ".join(headlines)
                }
            else:
                return {
                    "type": "text",
                    "data": "No news found at the moment"
                }

        except Exception as e:
            return {
                "type": "text",
                "data": "News service unavailable"
            }



    # 🤖 AI CHAT (LAST FALLBACK)
    completion = ai_client.chat.completions.create(
        model="Meta-Llama-3.3-70B-Instruct",
        messages=[
            {"role": "system", "content": "You are Friday, an intelligent assistant."},
            {"role": "user", "content": command}
        ]
    )

    return {"type": "text", "data": completion.choices[0].message.content}
