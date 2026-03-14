import urllib.parse
import uuid


POLLINATIONS_URL = "https://image.pollinations.ai/prompt/"


def generate_image(prompt):
    cleaned_prompt = prompt.strip()
    encoded_prompt = urllib.parse.quote(cleaned_prompt)
    seed = uuid.uuid4().hex[:8]
    return f"{POLLINATIONS_URL}{encoded_prompt}?width=1024&height=1024&seed={seed}"
