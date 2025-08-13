import asyncio
import sys
import os
from dotenv import load_dotenv
from contextlib import AsyncExitStack

from mcp_client import MCPClient
from core.gemini import Gemini

load_dotenv()

# Gemini Configuration
gemini_model = os.getenv("GEMINI_MODEL", "")
google_api_key = os.getenv("GOOGLE_API_KEY", "")

# Validate Gemini configuration
if not gemini_model:
    raise ValueError("Error: GEMINI_MODEL cannot be empty. Update .env file")
if not google_api_key:
    raise ValueError("Error: GOOGLE_API_KEY cannot be empty. Update .env file")

print(f"🚀 Starting Gemini Agent with model: {gemini_model}")
print("Type 'quit' to exit")
print("-" * 50)

async def main():
    # Initialize Gemini AI service
    ai_service_instance = Gemini(model=gemini_model)
    
    # Initialize MCP client
    command, args = (
        ("uv", ["run", "mcp_server.py"])
        if os.getenv("USE_UV", "0") == "1"
        else ("python", ["mcp_server.py"])
    )
    
    async with AsyncExitStack() as stack:
        mcp_client = await stack.enter_async_context(
            MCPClient(command=command, args=args)
        )
        
        print("✅ Connected to MCP server")
        print("✅ Ready to chat!")
        print()
        
        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                # Process the query
                print("🤖 Thinking...")
                response = await ai_service_instance.handle_user_query_with_tools(
                    user_query=user_input,
                    mcp_client=mcp_client,
                    system="You are a helpful AI assistant with access to document tools. Use tools when needed to provide accurate information.",
                    temperature=0.7
                )
                
                # Display response
                print(f"Assistant: {ai_service_instance.text_from_message(response)}")
                print()
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                print()

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
