import os
import requests
import webbrowser
from dotenv import load_dotenv
import uuid
load_dotenv()

API_URL = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"
HEADERS = {
    "Authorization": f"Bearer {os.getenv('HF_API_KEY')}",
    "Content-Type": "application/json"
}

def generate_image(prompt):
    print("🎨 Generating image... (first run may take time)")

    response = requests.post(
        API_URL,
        headers=HEADERS,
        json={"inputs": prompt},
        timeout=180
    )

    if response.status_code != 200:
        print("❌ Error:", response.status_code, response.text)
        return None

   

   # image_generator.py
    import os, uuid

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    IMAGE_DIR = os.path.join(BASE_DIR, "..", "backend", "images")

    os.makedirs(IMAGE_DIR, exist_ok=True)

    filename = f"{uuid.uuid4().hex}.png"
    image_path = os.path.join(IMAGE_DIR, filename)

    with open(image_path, "wb") as f:
        f.write(response.content)

    return image_path




# Optional: run standalone (for testing only)
if __name__ == "__main__":
    prompt = input("🖌️ Enter image prompt: ").strip()
    generate_image(prompt)
