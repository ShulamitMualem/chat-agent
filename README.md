# Gemini Agent with MCP Tools

A powerful AI agent built with Google Gemini that can interact with tools through the Model Context Protocol (MCP). This agent can read documents, edit them, and perform various tasks using an extensible tool system.

## Features

- **Gemini AI Integration**: Powered by Google's Gemini 2.5 Flash model
- **Tool Usage**: Automatically decides when and how to use available tools
- **Document Management**: Read and edit documents through MCP tools
- **Natural Conversations**: Responds naturally without technical jargon
- **Extensible Architecture**: Easy to add new tools and capabilities

## How It Works

The agent receives your question, analyzes it, and automatically:
1. **Decides** if tools are needed to answer your question
2. **Calls** the appropriate tools with correct parameters
3. **Processes** the results and provides a natural response
4. **Handles** errors gracefully with helpful messages

## Prerequisites

- Python 3.9+
- Google API Key (for Gemini)

## Setup

### Step 1: Configure the environment variables

1. Create or edit the `.env` file in the project root and verify that the following variables are set correctly:

```
GOOGLE_API_KEY="your-google-api-key-here"  # Enter your Google API key for Gemini
GEMINI_MODEL="gemini-2.5-flash"            # Model to use (default: gemini-2.5-flash)
```

### Step 2: Install dependencies

#### Option 1: Setup with uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package installer and resolver.

1. Install uv, if not already installed:

```bash
pip install uv
```

2. Create and activate a virtual environment:

```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:

```bash
uv pip install -e .
```

4. Run the project

```bash
uv run main.py
```

#### Option 2: Setup without uv

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install google-generativeai python-dotenv prompt-toolkit mcp
```

3. Run the project

```bash
python main.py
```

## Usage

### Running the Agent

You have two options to run the agent:

#### Option 1: Full CLI Interface (with prompt_toolkit)
```bash
python main.py
```

#### Option 2: Simple Interface
```bash
python simple_main.py
```

### Available Commands

The agent can understand natural language and automatically use tools when needed:

#### Reading Documents
```
> What's in the deposition document?
> Read the report file
> Show me the contents of plan.md
```

#### Editing Documents
```
> Change 'condenser tower' to 'cooling system' in the report
> Replace 'Angela Smith' with 'John Doe' in the deposition
> Update the plan document
```

#### General Questions
```
> Hello, how are you?
> What documents are available?
> Help me with document management
```

### Available Documents

The agent has access to these documents:
- `deposition.md` - Testimony documents
- `report.pdf` - Technical reports
- `financials.docx` - Financial documents
- `outlook.pdf` - Project outlook
- `plan.md` - Project plans
- `spec.txt` - Technical specifications

### Example Interactions

```
User: What's in the deposition document?
Agent: This deposition covers the testimony of Angela Smith, P.E.

User: Change 'condenser tower' to 'cooling system' in the report
Agent: Successfully completed the edit_document operation.

User: Hello, how are you?
Agent: Hello! I'm doing well, thank you for asking. How can I help you today?
```

## Development

### Project Structure

```
cli-project-gemini/
├── core/
│   ├── gemini.py          # Main Gemini agent implementation
│   ├── chat.py            # Base chat functionality
│   ├── cli_chat.py        # CLI-specific chat features
│   └── tools.py           # Tool management
├── mcp_server.py          # MCP server with document tools
├── mcp_client.py          # MCP client for tool communication
├── main.py                # Full CLI application
├── simple_main.py         # Simple interface
└── test_gemini_agent.py   # Testing script
```

### Adding New Tools

1. **Add tools to MCP server** (`mcp_server.py`):
```python
@mcp.tool(
    name="your_tool_name",
    description="Description of what your tool does"
)
def your_tool_function(param1: str, param2: str):
    # Your tool implementation
    return result
```

2. **Update system prompt** in `core/gemini.py` to include examples of your new tool

3. **Test the tool** using the testing scripts

### Adding New Documents

Edit the `docs` dictionary in `mcp_server.py`:

```python
docs = {
    "your_document.md": "Your document content here",
    # ... existing documents
}
```

### Testing

Run the test suite to verify everything works:

```bash
python test_gemini_agent.py
```

### Architecture

The agent uses a custom tool calling mechanism:
- **System Prompt**: Includes tool descriptions and usage examples
- **Tool Detection**: Parses `TOOL_CALL:` responses from Gemini
- **Parameter Parsing**: Extracts tool name and parameters from response
- **Execution**: Calls tools through MCP client
- **Response Handling**: Formats results for natural conversation

## Advanced Features

### Custom Tool Calling
The agent implements a custom `TOOL_CALL:` format that allows Gemini to specify which tools to use and with what parameters:

```
TOOL_CALL: tool_name:param1=value1,param2=value2
```

### Error Handling
- Graceful handling of tool execution errors
- Fallback responses when tools are unavailable
- Clear error messages for debugging

### Extensibility
- Easy to add new tools to the MCP server
- Flexible system prompt that can include new tool examples
- Modular architecture for easy maintenance

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add your tools to `mcp_server.py`
4. Update the system prompt in `core/gemini.py`
5. Test your changes
6. Submit a pull request

## License

This project is open source and available under the MIT License.
