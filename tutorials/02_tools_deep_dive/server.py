"""Tutorial 02 — Tools Deep Dive: Multiple tools with varied signatures."""

import json

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ToolsDeepDive")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two integers and return the sum."""
    return a + b


@mcp.tool()
def calculate_bmi(weight_kg: float, height_m: float) -> str:
    """Calculate Body Mass Index from weight (kg) and height (m).

    Returns a formatted string with the BMI value and category.
    """
    if height_m <= 0:
        return "Error: height must be positive."
    if weight_kg <= 0:
        return "Error: weight must be positive."

    bmi = weight_kg / (height_m ** 2)

    if bmi < 18.5:
        category = "underweight"
    elif bmi < 25:
        category = "normal weight"
    elif bmi < 30:
        category = "overweight"
    else:
        category = "obese"

    return f"BMI: {bmi:.1f} ({category})"


@mcp.tool()
def count_words(text: str) -> str:
    """Analyse text and return word count, character count, and line count.

    Returns a JSON string with the keys: word_count, char_count, line_count.
    """
    words = text.split()
    result = {
        "word_count": len(words),
        "char_count": len(text),
        "line_count": text.count("\n") + 1 if text else 0,
    }
    return json.dumps(result)


@mcp.tool()
def format_list(items: list[str], numbered: bool = False) -> str:
    """Format a list of strings as a bullet or numbered list.

    Args:
        items: The strings to format.
        numbered: If True, use numbered lines (1. 2. 3.) instead of bullets.
    """
    if not items:
        return "(empty list)"

    lines = []
    for i, item in enumerate(items, start=1):
        prefix = f"{i}." if numbered else "-"
        lines.append(f"{prefix} {item}")
    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run()
