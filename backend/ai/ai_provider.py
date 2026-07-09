import os
from google import genai

def generate_ai_response(prompt: str) -> str:
    """
    Sends the prompt to Google Gemini API (model: gemini-2.5-flash) and returns the plain text response.
    Catches all exceptions and missing key errors, returning a graceful fallback response.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "I'm running in offline mode because no GEMINI_API_KEY is configured. I can still help you open websites, search the web, play music, set reminders, and show weather/news!"

    try:
        # Initialize GenAI Client using the Google GenAI SDK
        client = genai.Client(api_key=api_key)
        
        # System instruction is passed as system_instruction in config or prepended.
        # In Google GenAI SDK, we can pass system_instruction in config:
        # response = client.models.generate_content(
        #     model="gemini-2.5-flash",
        #     contents=prompt,
        #     config=types.GenerateContentConfig(system_instruction="...")
        # )
        # Since we just need content generation, let's keep it simple:
        system_prefix = "You are F.R.I.D.A.Y, an intelligent virtual assistant. Give clear, concise answers. If user speaks Hindi, reply in Hindi. Otherwise reply in English.\n\n"
        full_prompt = f"{system_prefix}User: {prompt}"
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=full_prompt
        )
        
        if response and response.text:
            return response.text.strip()
        else:
            return "I'm unable to reach the AI service right now. Please try again in a moment."
            
    except Exception as e:
        # Log or print exception internally, but return user-friendly fallback
        print(f"Gemini API Error: {str(e)}")
        return "I'm unable to reach the AI service right now. Please try again in a moment."
