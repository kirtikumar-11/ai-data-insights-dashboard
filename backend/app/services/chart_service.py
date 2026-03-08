"""
Chart Generation Engine — Inspects query results and determines the best visualization.
Returns chart configuration compatible with ECharts on the frontend.
"""
import re
from typing import Any


def generate_chart_config(
    columns: list[str],
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Analyze query result columns and data to determine the best chart type
    and return a configuration object for the frontend.
    """
    if not rows or not columns:
        return {"chart_type": "table", "data": rows}

    chart_type = _choose_chart_type(columns, rows)

    if chart_type == "table":
        return {
            "chart_type": "table",
            "columns": columns,
            "data": rows,
        }

    x_col = columns[0]
    y_col = columns[1] if len(columns) > 1 else columns[0]

    # Extract x and y data
    x_data = [str(row[x_col]) for row in rows]
    y_data = [_to_number(row[y_col]) for row in rows]

    config = {
        "chart_type": chart_type,
        "x_axis": x_col,
        "y_axis": y_col,
        "x_data": x_data,
        "y_data": y_data,
        "columns": columns,
        "data": rows,
    }

    # For pie charts, structure data differently
    if chart_type == "pie":
        config["pie_data"] = [
            {"name": str(row[x_col]), "value": _to_number(row[y_col])}
            for row in rows
        ]

    return config


def _choose_chart_type(columns: list[str], rows: list[dict]) -> str:
    """
    Determine chart type based on column names and data patterns.

    Rules from spec:
      - date/time column + metric → line chart
      - category + metric → bar chart
      - category with percentages → pie chart
      - fallback → table
    """
    if len(columns) < 2:
        return "table"

    first_col = columns[0].lower()
    second_col = columns[1].lower() if len(columns) > 1 else ""

    # Check if first column is a date/time field
    date_patterns = ["date", "timestamp", "month", "year", "day", "week", "quarter"]
    if any(pattern in first_col for pattern in date_patterns):
        return "line"

    # Check if second column is numeric (metric)
    if rows:
        second_val = rows[0].get(columns[1])
        is_numeric = isinstance(second_val, (int, float)) or _is_numeric_string(second_val)

        if is_numeric:
            # If few categories (≤ 8) → could be pie chart
            unique_values = len(set(str(row[columns[0]]) for row in rows))
            if unique_values <= 8 and len(rows) <= 8:
                # Check if values could represent proportions
                if _looks_like_proportions(rows, columns[1]):
                    return "pie"
            return "bar"

    return "table"


def _looks_like_proportions(rows: list[dict], value_col: str) -> bool:
    """Check if the values look like they represent parts of a whole."""
    try:
        values = [float(row[value_col]) for row in rows if row[value_col] is not None]
        if not values:
            return False
        # All positive values suggest proportions
        return all(v >= 0 for v in values)
    except (ValueError, TypeError):
        return False


def _to_number(val) -> float:
    """Convert a value to a number for chart rendering."""
    if val is None:
        return 0
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0


def _is_numeric_string(val) -> bool:
    """Check if a string can be parsed as a number."""
    if val is None:
        return False
    try:
        float(val)
        return True
    except (ValueError, TypeError):
        return False
