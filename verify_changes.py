import asyncio
import sys
import os
from dotenv import load_dotenv
from contextlib import AsyncExitStack

from mcp_client import MCPClient
from core.gemini import Gemini

load_dotenv()

async def verify_changes():
    # Initialize Gemini AI service
    gemini_model = os.getenv("GEMINI_MODEL", "")
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
        
        # Verify the changes
        print("Verifying document changes...")
        print("=" * 50)
        
        # Check report.pdf
        print("\n1. Checking report.pdf:")
        response = await ai_service_instance.handle_user_query_with_tools(
            user_query="What's in the report document?",
            mcp_client=mcp_client,
            system="You are a helpful AI assistant with access to document tools. Use tools when needed to provide accurate information.",
            temperature=0.7
        )
        print(f"Content: {ai_service_instance.text_from_message(response)}")
        
        # Check deposition.md
        print("\n2. Checking deposition.md:")
        response = await ai_service_instance.handle_user_query_with_tools(
            user_query="What's in the deposition document?",
            mcp_client=mcp_client,
            system="You are a helpful AI assistant with access to document tools. Use tools when needed to provide accurate information.",
            temperature=0.7
        )
        print(f"Content: {ai_service_instance.text_from_message(response)}")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(verify_changes())
