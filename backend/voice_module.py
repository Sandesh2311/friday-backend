from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

def hindi_to_english(text):
    """
    Transliterates Devnagari script to ITRANS format (English representation)
    so the assistant can interpret phonetic Hindi commands.
    """
    try:
        # Simple test to check if Devanagari script is present
        if any('\u0900' <= char <= '\u097F' for char in text):
            return transliterate(text, sanscript.DEVANAGARI, sanscript.ITRANS)
        return text
    except Exception:
        return text

def get_voice_config():
    """
    Returns default/recommended parameters for SpeechSynthesis on frontend
    """
    return {
        "default_lang": "en-IN",
        "fallback_lang": "hi-IN",
        "rate": 1.0,
        "pitch": 1.0
    }
