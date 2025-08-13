from typing import Dict, Any, Union
from core.gemini import Gemini
from mcp_client import MCPClient
from core.tools import ToolManager

MessageParam = Dict[str, Any]


class Chat:
    def __init__(self, ai_service: Gemini, clients: dict[str, MCPClient]):
        self.ai_service: Gemini = ai_service
        self.clients: dict[str, MCPClient] = clients
        self.messages: list[MessageParam] = []

    async def _process_query(self, query: str):
        self.messages.append({"role": "user", "content": query})

    async def run(
        self,
        query: str,
    ) -> str:
        print(f"[DEBUG] run called with query: {query}")  # Debug log
        
        # Check if this is a Gemini AI service that supports tools
        if hasattr(self.ai_service, 'handle_user_query_with_tools'):
            # Use the enhanced tool-aware processing
            response = await self.ai_service.handle_user_query_with_tools(
                user_query=query,
                mcp_client=list(self.clients.values())[0],  # Use the first client
                system="You are a helpful AI assistant with access to document tools. Use tools when needed to provide accurate information.",
                temperature=0.7
            )
            
            return self.ai_service.text_from_message(response)
        
        # Fallback to the original method for other AI services
        final_text_response = ""
        await self._process_query(query)

        while True:
            print("[DEBUG] Sending messages to AI service")  # Debug log
            response = await self.ai_service.chat(
                messages=self.messages,
                tools=await ToolManager.get_all_tools(self.clients),
            )

            print(f"[DEBUG] AI service response: {response}")  # Debug log
            print(f"[DEBUG] Full Gemini response content: {response.content}")  # Debug log

            self.ai_service.add_assistant_message(self.messages, response)

            if hasattr(response, 'stop_reason') and response.stop_reason == "tool_use":
                print("[DEBUG] Tool use detected in response")  # Debug log
                print(self.ai_service.text_from_message(response))
                tool_result_parts = await ToolManager.execute_tool_requests(
                    self.clients, response
                )

                print(f"[DEBUG] Tool result parts: {tool_result_parts}")  # Debug log
                self.ai_service.add_user_message(
                    self.messages, tool_result_parts
                )
            else:
                print("[DEBUG] No tool use detected in response")  # Debug log
                final_text_response = self.ai_service.text_from_message(
                    response
                )
                break

        return final_text_response
