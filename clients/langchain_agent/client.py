"""LangChain ReAct agent with MCP tools.

Uses langchain-mcp-adapters to load MCP tools as LangChain tools,
then builds a ReAct agent with LangGraph for reasoning + acting.
"""

import asyncio
import os

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def run_agent(
    server_script: str = "tutorials/02_tools_deep_dive/server.py",
    query: str = "What is 42 + 58?",
):
    """Run a LangChain ReAct agent with MCP tools."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Set ANTHROPIC_API_KEY to use this client.")
        return

    model = ChatAnthropic(model="claude-sonnet-4-20250514", api_key=api_key)

    server_params = StdioServerParameters(
        command="uv",
        args=["run", "python", server_script],
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            # Load MCP tools as LangChain tools
            tools = await load_mcp_tools(session)
            print(f"Loaded {len(tools)} tools:")
            for tool in tools:
                print(f"  - {tool.name}: {tool.description}")

            # Create ReAct agent
            agent = create_react_agent(model, tools)

            # Run
            print(f"\nQuery: {query}")
            result = await agent.ainvoke({"messages": [HumanMessage(content=query)]})

            # Print final message
            final_message = result["messages"][-1]
            print(f"\nAgent: {final_message.content}")


if __name__ == "__main__":
    asyncio.run(run_agent())
