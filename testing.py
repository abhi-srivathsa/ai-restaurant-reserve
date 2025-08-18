import google.generativeai as genai
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("Error: Please set GEMINI_API_KEY environment variable")
    exit(1)

genai.configure(api_key=GEMINI_API_KEY)
print("hi")
for m in genai.list_models():
    print(m.name)
