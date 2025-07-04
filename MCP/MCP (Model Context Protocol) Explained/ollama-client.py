"""
Employee Database MCP Client

A client application for interacting with the Employee Database Management System
using the Model Context Protocol (MCP) and LlamaIndex framework.
"""

# Configure the language model
language_model = Ollama(model="llama3-groq-tool-use:8b", request_timeout=120.0)
Settings.llm = language_model
import asyncio
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
from llama_index.core.agent.workflow import FunctionAgent, ToolCallResult, ToolCall
from llama_index.core.workflow import Context
from llama_index.llms.ollama import Ollama
from llama_index.core import Settings

llm = Ollama(model="llama3-groq-tool-use:8b", request_timeout=120.0)
Settings.llm = llm


# System prompt for the agent
SYSTEM_PROMPT = """\
You are an AI assistant specialized in Employee Database Management.

Your primary role is to help users interact with our Employee Database system using the available tools.
You can insert new employee records and retrieve existing employee information based on user requests.
Always ensure data integrity and provide helpful responses about database operations.
"""

async def create_database_agent(tool_specification: McpToolSpec):
    """Create and configure a FunctionAgent for database operations."""
    available_tools = await tool_specification.to_tool_list_async()
    
    database_agent = FunctionAgent(
        name="EmployeeDatabaseAgent",
        description="An intelligent agent for managing employee database operations and queries.",
        tools=available_tools,
        llm=language_model,
        system_prompt=SYSTEM_PROMPT,
    )
    return database_agent

async def process_user_request(
    user_message: str,
    database_agent: FunctionAgent,
    agent_context: Context,
    show_details: bool = False,
):
    """Process and handle user requests through the database agent."""
    request_handler = database_agent.run(user_message, ctx=agent_context)
    
    async for event in request_handler.stream_events():
        if show_details and type(event) == ToolCall:
            print(f"🔧 Executing tool: {event.tool_name} with parameters: {event.tool_kwargs}")
        elif show_details and type(event) == ToolCallResult:
            print(f"✅ Tool '{event.tool_name}' completed with result: {event.tool_output}")

    final_response = await request_handler
    return str(final_response)

async def main():
    """Main execution function for the Employee Database Client."""
    # Initialize MCP client and tool specification
    mcp_client = BasicMCPClient("http://127.0.0.1:8000/sse")
    mcp_tool_spec = McpToolSpec(client=mcp_client)
    
    # Create the database agent
    database_agent = await create_database_agent(mcp_tool_spec)
    
    # Initialize agent context
    agent_context = Context(database_agent)
    
    # Display available database operations
    available_tools = await mcp_tool_spec.to_tool_list_async()
    print("🗄️  Employee Database Management System")
    print("=" * 50)
    print("Available database operations:")
    for tool in available_tools:
        print(f"📋 {tool.metadata.name}: {tool.metadata.description}")
    
    # Interactive session
    print("\n💬 Interactive Mode - Type 'quit' or 'exit' to terminate")
    print("=" * 50)
    
    while True:
        try:
            user_request = input("\n👤 Your request: ")
            if user_request.lower() in ["exit", "quit", "q"]:
                print("👋 Goodbye! Database session terminated.")
                break
                
            print(f"\n📝 Processing: {user_request}")
            agent_response = await process_user_request(
                user_request, database_agent, agent_context, show_details=True
            )
            print(f"🤖 Agent Response: {agent_response}")
            
        except KeyboardInterrupt:
            print("\n\n🛑 Session interrupted by user. Exiting...")
            break
        except Exception as error:
            print(f"❌ An error occurred: {str(error)}")
            print("🔄 Please try again or check your server connection.")

if __name__ == "__main__":
    asyncio.run(main()) 