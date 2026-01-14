import speech_recognition as sr
import webbrowser
import pyttsx3
import musicLibrary
import requests
from openai import OpenAI
from openai import OpenAI
# from gtts import gTTS
# from playsound import playsound
import urllib.parse
# import uuid
# import os
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
import yt_dlp
from image_generator import generate_image

engine = pyttsx3.init()
engine.setProperty("rate", 190)     # speed (try 180–200)
engine.setProperty("volume", 1.0)   # full volume

# Optional: force female voice if available
voices = engine.getProperty("voices")
for v in voices:
    if "zira" in v.name.lower():
        engine.setProperty("voice", v.id)
        break


ai_client = OpenAI(
    base_url="https://api.sambanova.ai/v1",
    api_key="98386aea-570b-4c45-90ec-7c2fe7f35887"
)

#song search yt function

def play_on_youtube(query):
    search_query = urllib.parse.quote(query)
    url = f"https://www.youtube.com/results?search_query={search_query}"
    
    webbrowser.open(url)


def play_youtube_first(query):
   

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,   # 🔥 hides ALL warnings
        "default_search": "ytsearch1",
        "skip_download": True,
        "format": "bestaudio/best",
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)
        video_url = info["entries"][0]["webpage_url"]

    webbrowser.open(video_url)




def hindi_to_english(text):
    try:
        return transliterate(text, sanscript.DEVANAGARI, sanscript.ITRANS)
    except:
        return text
def normalize_command(c):
    replacements = {
        "न्यूज़": "news",
        "खबर": "news",
        "खबरें": "news",
        "समाचार": "news"
    }

    for hindi, eng in replacements.items():
        c = c.replace(hindi, eng)

    return c


recognizer = sr.Recognizer()
engine = pyttsx3.init()
newsapi = "2646fc30f2fd4ef49a82ace817da207a"




def speak(text):
    engine.say(text)
    engine.runAndWait()



def aiProcess(command):
    completion = ai_client.chat.completions.create(
        model="Meta-Llama-3.3-70B-Instruct",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a virtual assistant named Friday skilled in general tasks like Alexa and Google Cloud."
                    "Give short responses. "
                    "If user speaks Hindi, reply in Hindi. "
                    "Otherwise reply in English."
                )
            },
            {"role": "user", "content": command}
        ]
    )
    return completion.choices[0].message.content



    
def processCommand(c):
    c = c.lower()

    # -------- OPEN WEBSITES --------
    if "open google" in c or "google kholo" in c or "google khol" in c:
      
        webbrowser.open("https://google.com")
        return

    elif "open youtube" in c or "youtube kholo" in c or "youtube khol" in c:
      
        webbrowser.open("https://youtube.com")
        return

    elif "open facebook" in c or "facebook kholo" in c or "facebook khol" in c:
       
        webbrowser.open("https://facebook.com")
        return

    elif "open linkedin" in c or "linkedin kholo" in c or "linkedin khol" in c:
       
        webbrowser.open("https://linkedin.com")
        return

    # -------- Songss --------
    elif (
        c.startswith("play")
        or "gaana chala" in c
        or "गाना चला" in c
        or "song chala" in c
        or "music chala" in c
    ):
        words = c.split()

        # 1️ Try local library
        for word in words:
            eng_word = hindi_to_english(word).lower()
            if eng_word in musicLibrary.music:
               
                webbrowser.open(musicLibrary.music[eng_word])
                return

        # 2️ YouTube autoplay fallback
        ignore_words = {
            "play", "song", "music", "gaana", "chala", "chalao",
            "बजाओ", "चलाओ", "गाना"
        }

        query_words = [
            hindi_to_english(w)
            for w in words
            if w not in ignore_words
        ]

        query = " ".join(query_words).strip()

        if query:
            play_youtube_first(query)
        else:
            speak("Kaunsa gaana chalaana hai?")
        return

    # -------- NEWSSS --------
    elif any(word in c for word in [
        "news", "khabar", "खबर", "samachar",
        "समाचार", "khabrein", "खबरें"
    ]):
        speak("Today top headlines are")

        r = requests.get(
            "https://newsapi.org/v2/everything?q=india&language=en&sortBy=publishedAt&apiKey=2646fc30f2fd4ef49a82ace817da207a"
        )

        if r.status_code == 200:
            for article in r.json().get("articles", [])[:5]:
                speak(article["title"])
        return

    # -------- STOP --------
    elif "stop" in c or "band" in c or "exit" in c:
        speak("Friday band ho rahi hai")
        exit()
    
    #-------- image------
    elif (
    "image" in c
    and any(k in c for k in [
        "generate", "create", "make", "draw",
        "bana", "bana do"
    ])
):
        prompt = c

        remove_words = [
            "generate", "create", "make", "draw",
            "an", "a", "image", "picture",
            "bana", "bana do", "tasveer"
        ]

        for w in remove_words:
            prompt = prompt.replace(w, "")

        prompt = prompt.strip()

        if not prompt:
            speak("Please tell me what image to generate")
            return

        speak("Generating image, please wait")
        generate_image(prompt)
        return

    # -------- AI FALLBACK --------
    else:
        output = aiProcess(c)
        speak(output)
     


if __name__ == "__main__":
    speak("Initializing Friday")
    
    r = sr.Recognizer()

    while True:
        try:
            with sr.Microphone() as source:
                print("Listening for wake word...")
                r.adjust_for_ambient_noise(source, duration=0.5)
                audio = r.listen(source)

                word = r.recognize_google(audio, language="en-IN")
                print("Heard:", word)

                wake_words = ["friday", "fridai", "fri day", "fri da", "friday"]

                if any(w in word.lower() for w in wake_words):
                    speak("Yes")


                with sr.Microphone() as source:
                    print("F.R.I.D.A.Y Active...")
                    r.adjust_for_ambient_noise(source, duration=0.5)
                    audio = r.listen(source, phrase_time_limit=5)

                try:
                    command = r.recognize_google(audio, language="en-IN")
                    print("Command (EN):", command)

                except sr.UnknownValueError:
                    command = r.recognize_google(audio, language="hi-IN")
                    print("Command (HI):", command)

                processCommand(command)

        except sr.WaitTimeoutError:
            print("Listening timeout")
        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as e:
            print("Speech service error:", e)
        except Exception as e:
            print("Error:", e)
