# Tutorial 02 — Tools Deep Dive

Four tools that demonstrate how FastMCP turns Python type hints into a
fully-described JSON Schema that any AI client can understand.

## Type hints become JSON Schema

FastMCP inspects every parameter's type annotation and builds the
`inputSchema` that MCP clients receive when they call `tools/list`.

| Python type      | JSON Schema type          | Example             |
|------------------|---------------------------|---------------------|
| `str`            | `{"type": "string"}`      | `message: str`      |
| `int`            | `{"type": "integer"}`     | `a: int`            |
| `float`          | `{"type": "number"}`      | `weight_kg: float`  |
| `bool`           | `{"type": "boolean"}`     | `numbered: bool`    |
| `list[str]`      | `{"type": "array", "items": {"type": "string"}}` | `items: list[str]` |

The AI sees this schema and knows exactly what arguments to provide, without
you writing any serialization code.

## Automatic schema generation

When you write:

```python
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two integers and return the sum."""
    return a + b
```

FastMCP generates:

```json
{
  "name": "add",
  "description": "Add two integers and return the sum.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "a": { "type": "integer" },
      "b": { "type": "integer" }
    },
    "required": ["a", "b"]
  }
}
```

The docstring becomes the description. Every parameter without a default value
goes into the `required` array.

## Optional parameters and defaults

```python
@mcp.tool()
def format_list(items: list[str], numbered: bool = False) -> str:
    ...
```

Because `numbered` has a default value of `False`, it is **not** included in
`required`. The AI can omit it, and your function receives the default. This is
how you design tools with sensible defaults that keep simple calls simple.

## Return types

MCP tools always return content to the client as a list of `TextContent`
objects. FastMCP handles conversion automatically:

| Python return | What the client sees                          |
|---------------|-----------------------------------------------|
| `str`         | Returned as-is in `TextContent.text`          |
| `int`/`float` | Converted to its string representation        |
| `dict`/`list` | Serialized to JSON string                     |

For `count_words`, we explicitly return `json.dumps(result)` so the structure
is clear, but returning a plain `dict` would also work.

## The tools in this tutorial

| Tool             | Parameters                          | Returns  |
|------------------|-------------------------------------|----------|
| `add`            | `a: int`, `b: int`                  | `int`    |
| `calculate_bmi`  | `weight_kg: float`, `height_m: float` | `str`  |
| `count_words`    | `text: str`                         | JSON `str` |
| `format_list`    | `items: list[str]`, `numbered: bool = False` | `str` |

## Running

```bash
# Inspector UI
mcp dev tutorials/02_tools_deep_dive/server.py

# Tests
uv run pytest tutorials/02_tools_deep_dive/ -v
```

## Next steps

Head to [Tutorial 03 — Resources](../03_resources/) to learn how to expose
read-only data through MCP resources and resource templates.
