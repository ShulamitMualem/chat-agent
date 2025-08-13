import asyncio
import sys
import os
from dotenv import load_dotenv
from contextlib import AsyncExitStack

from mcp_client import MCPClient
from core.gemini import Gemini

load_dotenv()

async def test_gemini_agent():
    """Test the Gemini agent with MCP tools"""
    
    # Check if Gemini is configured
    gemini_model = os.getenv("GEMINI_MODEL", "")
    google_api_key = os.getenv("GOOGLE_API_KEY", "")
    
    if not gemini_model or not google_api_key:
        print("Error: GEMINI_MODEL and GOOGLE_API_KEY must be set in .env file")
        return
    
    # Initialize Gemini
    gemini = Gemini(model=gemini_model)
    
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
        
        # Test queries
        test_queries = [
            "What's in the deposition document?",
            "Read the financials document",
            "Hello, how are you?",
            "What documents are available?",
            "Edit the plan document to add a new section about testing"
        ]
        
        for query in test_queries:
            print(f"\n{'='*50}")
            print(f"Testing query: {query}")
            print(f"{'='*50}")
            
            try:
                response = await gemini.handle_user_query_with_tools(
                    user_query=query,
                    mcp_client=mcp_client,
                    system="You are a helpful AI assistant with access to document tools. Use tools when needed to provide accurate information.",
                    temperature=0.7
                )
                
                print(f"Response: {gemini.text_from_message(response)}")
                
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(test_gemini_agent())
