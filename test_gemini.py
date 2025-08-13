import os
import asyncio
from dotenv import load_dotenv
from core.gemini import Gemini
from core.claude import Claude

# Load environment variables
load_dotenv()

# Get configuration
ai_service = os.getenv("AI_SERVICE", "gemini").lower()
gemini_model = os.getenv("GEMINI_MODEL", "")
google_api_key = os.getenv("GOOGLE_API_KEY", "")
claude_model = os.getenv("CLAUDE_MODEL", "")
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")

print(f"AI Service: {ai_service}")

if ai_service == "gemini":
    print(f"Gemini Model: {gemini_model}")
    print(f"Google API Key: {'*' * 10 + google_api_key[-4:] if google_api_key else 'Not set'}")
    
    # Initialize Gemini service
    ai_service_instance = Gemini(model=gemini_model)
else:
    print(f"Claude Model: {claude_model}")
    print(f"Anthropic API Key: {'*' * 10 + anthropic_api_key[-4:] if anthropic_api_key else 'Not set'}")
    
    # Initialize Claude service
    ai_service_instance = Claude(model=claude_model)

# Test a simple chat
messages = []
ai_service_instance.add_user_message(messages, "Hello! Can you tell me a short joke?")

try:
    response = ai_service_instance.chat(messages)
    print(f"\nResponse from {ai_service.title()}:")
    print(ai_service_instance.text_from_message(response))
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()