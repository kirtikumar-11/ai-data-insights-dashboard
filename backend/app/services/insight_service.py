"""
Insight Generation Service — Summarizes query results and sends them
to the LLM for a short business insight.
"""
from typing import Any


def build_data_summary(
    columns: list[str],
    rows: list[dict[str, Any]],
    max_rows: int = 20,
) -> str:
    """
    Build a concise text summary of the query results
    suitable for sending to the LLM for insight generation.
    """
    if not rows:
        return "No data returned."

    lines = []
    lines.append(f"Columns: {', '.join(columns)}")
    lines.append(f"Total rows: {len(rows)}")
    lines.append("")

    # Show up to max_rows of data
    display_rows = rows[:max_rows]
    for i, row in enumerate(display_rows, 1):
        row_str = " | ".join(f"{col}: {row.get(col, 'N/A')}" for col in columns)
        lines.append(f"Row {i}: {row_str}")

    if len(rows) > max_rows:
        lines.append(f"... and {len(rows) - max_rows} more rows")

    return "\n".join(lines)
