import google.generativeai as genai
from typing import List, Dict, Any, Optional
import json
import re
import ast


class GeminiMessage:
    """Wrapper class to mimic Anthropic's Message structure"""
    def __init__(self, content, role="assistant", stop_reason=None):
        self.content = content if isinstance(content, list) else [TextBlock(content)]
        self.role = role
        self.stop_reason = stop_reason


class TextBlock:
    """Wrapper class to mimic Anthropic's text block structure"""
    def __init__(self, text):
        self.text = text
        self.type = "text"

class ToolUseBlock:
    """Wrapper class to mimic tool use in messages"""
    def __init__(self, id, name, input):
        self.id = id
        self.name = name
        self.input = input
        self.type = "tool_use"

class Gemini:
    def __init__(self, model: str):
        self.model_name = model
        genai.configure()  # API key will be configured from environment
        
        # Configure generation settings
        self.generation_config = genai.GenerationConfig(
            max_output_tokens=8000,
            temperature=0.7,
        )
        
        # Initialize the model
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=self.generation_config
        )

    def add_user_message(self, messages: list, message):
        user_message = {
            "role": "user",
            "content": message.content
            if isinstance(message, GeminiMessage)
            else message,
        }
        messages.append(user_message)

    def add_assistant_message(self, messages: list, message):
        assistant_message = {
            "role": "assistant",
            "content": message.content
            if isinstance(message, GeminiMessage)
            else message,
        }
        messages.append(assistant_message)

    def text_from_message(self, message: GeminiMessage):
        if isinstance(message, GeminiMessage):
            return "\n".join(
                [block.text for block in message.content if hasattr(block, 'type') and block.type == "text"]
            )
        return str(message)

    def _convert_messages_for_gemini(self, messages: List[Dict], system: Optional[str] = None):
        """Convert message format from Anthropic style to Gemini style"""
        gemini_messages = []
        
        # Add system message if present
        if system:
            gemini_messages.append({
                "role": "user",
                "parts": [f"System: {system}"]
            })
            gemini_messages.append({
                "role": "model",
                "parts": ["Understood. I'll follow these instructions."]
            })
        
        # Convert each message
        for msg in messages:
            role = "model" if msg["role"] == "assistant" else msg["role"]
            
            # Handle content that might be a list or string
            content = msg["content"]
            if isinstance(content, list):
                # Extract text from content blocks
                text_parts = []
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        text_parts.append(block["text"])
                    elif isinstance(block, dict) and "text" in block:
                        text_parts.append(block["text"])
                    elif hasattr(block, "text"):
                        text_parts.append(block.text)
                    else:
                        text_parts.append(str(block))
                content = "\n".join(text_parts)
            
            gemini_messages.append({
                "role": role,
                "parts": [content]
            })
        
        return gemini_messages

    def _create_tool_system_prompt(self, tools: List[Any]) -> str:
        """Create a system prompt that includes tool descriptions and usage instructions"""
        tool_descriptions = []
        
        for tool in tools:
            # Extract tool information
            tool_name = getattr(tool, 'name', str(tool))
            tool_description = getattr(tool, 'description', 'No description available')
            
            # Extract parameters if available
            parameters = getattr(tool, 'inputSchema', {})
            if hasattr(parameters, 'properties'):
                param_descriptions = []
                for param_name, param_info in parameters.properties.items():
                    param_desc = getattr(param_info, 'description', 'No description')
                    param_descriptions.append(f"  - {param_name}: {param_desc}")
                params_text = "\n".join(param_descriptions)
            else:
                params_text = "  - No specific parameters documented"
            
            tool_descriptions.append(f"""
Tool: {tool_name}
Description: {tool_description}
Parameters:
{params_text}
""")
        
        tools_text = "\n".join(tool_descriptions)
        
        return f"""You are a helpful AI assistant with access to the following tools:

{tools_text}

Available documents: deposition.md, report.pdf, financials.docx, outlook.pdf, plan.md, spec.txt

When a user asks a question:
1. If you need to use a tool to answer, respond with: TOOL_CALL: tool_name:param1=value1,param2=value2
2. If you don't need tools, answer naturally and conversationally

Examples:
- User: "What's in the deposition document?"
  Assistant: TOOL_CALL: read_doc_contents:doc_id=deposition.md

- User: "Change 'condenser tower' to 'cooling system' in the report"
  Assistant: TOOL_CALL: edit_document:doc_id=report.pdf,old_str=condenser tower,new_str=cooling system

- User: "Hello, how are you?"
  Assistant: Hello! I'm doing well, thank you for asking. How can I help you today?

Don't refer to or mention the provided context in any way - just use it to inform your answer.
"""

    async def chat(
        self,
        messages,
        system=None,
        temperature=0.7,
        stop_sequences=None,
        tools=None,
        thinking=False,
        thinking_budget=1024,
        mcp_client=None,
    ) -> GeminiMessage:
        print(f"[DEBUG] chat called with messages: {messages}, system: {system}, temperature: {temperature}, stop_sequences: {stop_sequences}, tools: {tools}, thinking: {thinking}, thinking_budget: {thinking_budget}")
        
        # Update generation config with temperature
        self.generation_config.temperature = temperature

        if stop_sequences:
            self.generation_config.stop_sequences = stop_sequences

        # Create enhanced system prompt with tool information
        enhanced_system = system or ""
        if tools:
            tool_system_prompt = self._create_tool_system_prompt(tools)
            enhanced_system = f"{enhanced_system}\n\n{tool_system_prompt}" if enhanced_system else tool_system_prompt

        # Convert messages to Gemini format
        gemini_messages = self._convert_messages_for_gemini(messages, enhanced_system)

        # Create chat session
        chat = self.model.start_chat(history=gemini_messages[:-1] if gemini_messages else [])

        # Get the last message to send
        if gemini_messages:
            last_message = gemini_messages[-1]["parts"][0]
        else:
            last_message = ""

        # Generate response
        response = chat.send_message(last_message)
        print(f"[DEBUG] Full Gemini response content: {response}")
        
        response_text = response.text if hasattr(response, 'text') else str(response)
        
        # Check for tool call in the response
        tool_call_match = re.search(r'TOOL_CALL:\s*(.+)', response_text)
        
        if tool_call_match:
            try:
                # Parse the tool call in format: tool_name:param1=value1,param2=value2
                tool_call_str = tool_call_match.group(1).strip()
                print(f"[DEBUG] Tool call string: {tool_call_str}")
                
                # Split into tool name and parameters
                if ':' in tool_call_str:
                    tool_name, params_str = tool_call_str.split(':', 1)
                    tool_name = tool_name.strip()
                    
                    # Parse parameters
                    tool_parameters = {}
                    if params_str:
                        param_pairs = params_str.split(',')
                        for pair in param_pairs:
                            if '=' in pair:
                                key, value = pair.split('=', 1)
                                tool_parameters[key.strip()] = value.strip()
                else:
                    tool_name = tool_call_str.strip()
                    tool_parameters = {}
                
                print(f"[DEBUG] Detected tool call: {tool_name} with parameters {tool_parameters}")
                
                # Execute the tool if available
                if tools and tool_name:
                    # Find the tool in the tools list
                    tool_function = None
                    for tool in tools:
                        if getattr(tool, 'name', str(tool)) == tool_name:
                            tool_function = tool
                            break
                    
                    if tool_function:
                        # Execute the tool using MCP client
                        print(f"[DEBUG] Executing tool {tool_name} with parameters {tool_parameters}")
                        tool_result = await mcp_client.call_tool(tool_name, tool_parameters)
                        
                        print(f"[DEBUG] Tool execution result: {tool_result}")
                        
                        # Create response with tool result
                        content_blocks = [
                            ToolUseBlock(
                                id=f"tool_{hash(str(tool_parameters))}",
                                name=tool_name,
                                input=tool_parameters
                            ),
                            TextBlock(f"Tool Result: {tool_result}\n\nBased on the tool result, here's the answer to your question:")
                        ]
                        
                        return GeminiMessage(content_blocks, stop_reason="tool_use")
                    else:
                        print(f"[DEBUG] Tool {tool_name} not found in available tools")
                        return GeminiMessage([TextBlock(f"Sorry, I couldn't find the tool '{tool_name}' that I tried to use. Let me provide a direct answer instead.")])
                        
            except json.JSONDecodeError as e:
                print(f"[DEBUG] Failed to parse tool call JSON: {e}")
                return GeminiMessage([TextBlock("I encountered an error while trying to use a tool. Let me provide a direct answer instead.")])
        
        # If no tool call detected, return the regular response
        return GeminiMessage([TextBlock(response_text)])

    async def handle_user_query_with_tools(
        self,
        user_query: str,
        mcp_client,
        system=None,
        temperature=0.7,
        stop_sequences=None,
    ) -> GeminiMessage:
        """
        Handle a user query, check if a tool is needed, and use it if required.

        Args:
            user_query: The user's input query.
            mcp_client: An instance of MCPClient to interact with tools.
            system: Optional system instructions.
            temperature: Sampling temperature for response generation.
            stop_sequences: Sequences to stop generation.

        Returns:
            GeminiMessage: The response from Gemini, including tool results if applicable.
        """
        try:
            # Step 1: Get the list of tools from the MCP client
            tools = await mcp_client.list_tools()
            print(f"[DEBUG] Available tools: {[tool.name for tool in tools]}")

            # Step 2: Prepare the initial messages for Gemini
            messages = [
                {"role": "user", "content": user_query}
            ]

            # Step 3: Generate a response from Gemini to determine if a tool is needed
            response = await self.chat(
                messages=messages,
                system=system,
                temperature=temperature,
                stop_sequences=stop_sequences,
                tools=tools,
                mcp_client=mcp_client,  # Pass MCP client to chat function
            )

            # Step 4: Check if the response indicates a tool use
            if response.stop_reason == "tool_use":
                for block in response.content:
                    if isinstance(block, ToolUseBlock):
                        tool_name = block.name
                        tool_input = block.input

                        print(f"[DEBUG] Executing tool: {tool_name} with input: {tool_input}")

                        # Step 5: Call the tool using the MCP client
                        tool_result = await mcp_client.call_tool(tool_name, tool_input)

                        # Step 6: Create a new response with the tool result
                        if tool_result and hasattr(tool_result, 'content'):
                            # Extract text from TextContent objects
                            if isinstance(tool_result.content, list):
                                text_parts = []
                                for content_item in tool_result.content:
                                    if hasattr(content_item, 'text'):
                                        text_parts.append(content_item.text)
                                    else:
                                        text_parts.append(str(content_item))
                                result_content = '\n'.join(text_parts)
                            else:
                                result_content = str(tool_result.content)
                        else:
                            result_content = str(tool_result)

                        # If the tool result is empty (like edit_document), provide a success message
                        if not result_content or result_content.strip() == "":
                            return GeminiMessage(
                                content=[
                                    TextBlock(f"Successfully completed the {tool_name} operation.")
                                ],
                                role="assistant"
                            )
                        else:
                            return GeminiMessage(
                                content=[
                                    TextBlock(f"{result_content}")
                                ],
                                role="assistant"
                            )

            # Step 7: Return the original response if no tool was used
            return response

        except Exception as e:
            print(f"[DEBUG] Error in handle_user_query_with_tools: {e}")
            return GeminiMessage(
                content=[TextBlock(f"I encountered an error while processing your request: {str(e)}. Please try again.")],
                role="assistant"
            )