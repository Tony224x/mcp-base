"""Claude API client — Bridge MCP tools into Claude's tool_use feature.

Demonstrates the full agent loop:
1. Connect to an MCP server and discover tools
2. Convert MCP tool schemas to Claude API format
3. Send user messages with tools to Claude
4. Handle tool_use responses by calling MCP tools
5. Return tool results to Claude for a final answer
"""

import asyncio
import json
import os

import anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def mcp_tool_to_claude_tool(tool) -> dict:
    """Convert an MCP tool definition to Claude API tool format."""
    return {
        "name": tool.name,
        "description": tool.description or "",
        "input_schema": tool.inputSchema,
    }


async def agent_loop(
    server_script: str,
    user_message: str,
    model: str = "claude-sonnet-4-20250514",
    max_turns: int = 5,
):
    """Run an agent loop: user -> Claude -> tool calls -> Claude -> final response."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Set ANTHROPIC_API_KEY to use this client.")
        return

    client = anthropic.Anthropic(api_key=api_key)

    server_params = StdioServerParameters(
        command="uv",
        args=["run", "python", server_script],
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            # Get available tools
            tools_result = await session.list_tools()
            claude_tools = [mcp_tool_to_claude_tool(t) for t in tools_result.tools]

            messages = [{"role": "user", "content": user_message}]

            for turn in range(max_turns):
                print(f"\n--- Turn {turn + 1} ---")
                response = client.messages.create(
                    model=model,
                    max_tokens=1024,
                    tools=claude_tools,
                    messages=messages,
                )

                # Check if Claude wants to use tools
                if response.stop_reason == "tool_use":
                    # Add assistant response to messages
                    messages.append({"role": "assistant", "content": response.content})

                    # Process each tool use
                    tool_results = []
                    for block in response.content:
                        if block.type == "tool_use":
                            print(f"  Calling tool: {block.name}({json.dumps(block.input)})")
                            mcp_result = await session.call_tool(block.name, block.input)
                            result_text = "\n".join(c.text for c in mcp_result.content)
                            print(f"  Result: {result_text[:200]}")
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": result_text,
                            })

                    messages.append({"role": "user", "content": tool_results})
                else:
                    # Final text response
                    for block in response.content:
                        if hasattr(block, "text"):
                            print(f"\nClaude: {block.text}")
                    break


if __name__ == "__main__":
    asyncio.run(
        agent_loop(
            server_script="tutorials/02_tools_deep_dive/server.py",
            user_message=(
                "What is 42 + 58? Also count the words in "
                "'The quick brown fox jumps over the lazy dog'."
            ),
        )
    )
