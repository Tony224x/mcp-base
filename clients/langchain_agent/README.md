# LangChain ReAct Agent with MCP Tools

Uses `langchain-mcp-adapters` to automatically convert MCP tools into LangChain tools, then builds a ReAct (Reasoning + Acting) agent with LangGraph.

## Architecture

```
User Query
    |
    v
LangGraph ReAct Agent
    |
    +--> Reason (Claude via ChatAnthropic)
    |        |
    |        v
    +--> Act (MCP tool via load_mcp_tools)
    |        |
    |        v
    +--> Observe (tool result)
    |        |
    |        v  (loop until done)
    +--> Final Answer
```

## Key Concepts

### load_mcp_tools

The `langchain-mcp-adapters` library provides `load_mcp_tools()` which takes a `ClientSession` and returns a list of LangChain `BaseTool` instances:

```python
from langchain_mcp_adapters.tools import load_mcp_tools

tools = await load_mcp_tools(session)
# Each tool has: .name, .description, .args_schema
# And can be called with: await tool.ainvoke({"param": "value"})
```

This handles all the schema conversion and async call bridging automatically.

### ReAct Agent

LangGraph's `create_react_agent()` creates an agent that alternates between:

1. **Reasoning** — The LLM analyzes the current state and decides what to do
2. **Acting** — The agent calls a tool based on the LLM's decision
3. **Observing** — The tool result is fed back to the LLM

```python
from langgraph.prebuilt import create_react_agent

agent = create_react_agent(model, tools)
result = await agent.ainvoke({"messages": [HumanMessage(content=query)]})
```

### Why LangChain + MCP?

- **Automatic conversion**: No manual schema mapping needed
- **Agent framework**: Built-in reasoning loop, memory, and error handling
- **Ecosystem**: Access to LangChain's tracing, evaluation, and deployment tools
- **Composability**: Combine MCP tools with other LangChain tools and chains

## Usage

```bash
export ANTHROPIC_API_KEY=sk-ant-...
uv run python clients/langchain_agent/client.py
```

## Tests

The tests validate tool loading without requiring an API key:

```bash
uv run pytest clients/langchain_agent/ -v
```

## Dependencies

Requires the `langchain` optional dependency group:

```bash
uv sync --extra langchain
```
