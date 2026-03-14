import os

import requests
import yt_dlp
from dotenv import load_dotenv
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
from openai import OpenAI

from project1_2.image_generator import generate_image
from project1_2.musicLibrary import music


load_dotenv()


def get_ai_client():
    api_key = os.getenv("SAMBANOVA_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    return OpenAI(
        base_url="https://api.sambanova.ai/v1",
        api_key=api_key,
    )


def hindi_to_english(text):
    try:
        return transliterate(text, sanscript.DEVANAGARI, sanscript.ITRANS)
    except Exception:
        return text


def friday_engine(command: str):
    c = command.lower()

    if "image" in c and any(k in c for k in ["generate", "create", "make", "draw", "bana"]):
        prompt = c
        for word in ["generate", "create", "make", "draw", "image", "picture", "bana"]:
            prompt = prompt.replace(word, "")
        prompt = prompt.strip()

        if not prompt:
            return {"type": "text", "data": "Please describe the image"}

        return {
            "type": "image",
            "data": generate_image(prompt),
        }

    if c.startswith("play") or "gaana" in c:
        words = c.split()

        for word in words:
            key = hindi_to_english(word).lower()
            if key in music:
                return {
                    "type": "action",
                    "data": music[key],
                }

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
                "skip_download": True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(query, download=False)
                video_url = info["entries"][0]["webpage_url"]

            return {
                "type": "action",
                "data": f"{video_url}&autoplay=1",
            }
        except Exception:
            return {
                "type": "action",
                "data": f"https://www.youtube.com/results?search_query={query}",
            }

    if "open google" in c or "google kholo" in c:
        return {"type": "action", "data": "https://google.com"}

    if "open youtube" in c or "youtube kholo" in c:
        return {"type": "action", "data": "https://youtube.com"}

    if "open facebook" in c:
        return {"type": "action", "data": "https://facebook.com"}

    if "open linkedin" in c:
        return {"type": "action", "data": "https://linkedin.com"}

    if "news" in c or "khabar" in c:
        news_api_key = os.getenv("NEWS_API_KEY")
        if not news_api_key:
            return {
                "type": "text",
                "data": "NEWS_API_KEY is not configured on the server.",
            }

        try:
            response = requests.get(
                "https://newsapi.org/v2/everything",
                params={
                    "q": "india",
                    "language": "en",
                    "sortBy": "publishedAt",
                    "apiKey": news_api_key,
                },
                timeout=10,
            )
            data = response.json()

            if data.get("articles"):
                headlines = [article["title"] for article in data["articles"][:5]]
                return {
                    "type": "text",
                    "data": " | ".join(headlines),
                }

            return {
                "type": "text",
                "data": "No news found at the moment",
            }
        except Exception:
            return {
                "type": "text",
                "data": "News service unavailable",
            }

    ai_client = get_ai_client()
    if ai_client is None:
        return {
            "type": "text",
            "data": "OPENAI_API_KEY or SAMBANOVA_API_KEY is not configured on the server.",
        }

    completion = ai_client.chat.completions.create(
        model="Meta-Llama-3.3-70B-Instruct",
        messages=[
            {"role": "system", "content": "You are Friday, an intelligent assistant."},
            {"role": "user", "content": command},
        ],
    )

    return {"type": "text", "data": completion.choices[0].message.content}
