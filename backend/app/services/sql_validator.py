"""
SQL Validation Layer — Ensures only safe, read-only queries are executed.
"""
import re


BLOCKED_KEYWORDS = [
    "DELETE", "UPDATE", "DROP", "ALTER",
    "INSERT", "TRUNCATE", "GRANT", "REVOKE",
    "CREATE", "EXEC", "EXECUTE",
]


class UnsafeSQLError(Exception):
    """Raised when the generated SQL contains disallowed operations."""
    pass


def validate_sql(sql: str) -> str:
    """
    Validate that the SQL query is safe to execute.
    Returns the cleaned SQL if valid, raises UnsafeSQLError otherwise.
    """
    if not sql or not sql.strip():
        raise UnsafeSQLError("Empty SQL query")

    normalized = sql.strip().upper()

    # Must start with SELECT or WITH (for CTEs)
    if not (normalized.startswith("SELECT") or normalized.startswith("WITH")):
        raise UnsafeSQLError(
            "Only SELECT queries are allowed. "
            f"Query starts with: {normalized[:20]}..."
        )

    # Check for blocked keywords as whole words
    for keyword in BLOCKED_KEYWORDS:
        pattern = rf"\b{keyword}\b"
        if re.search(pattern, normalized):
            raise UnsafeSQLError(
                f"Unsafe SQL detected: '{keyword}' is not allowed."
            )

    # Block multiple statements (semicolons in the middle)
    # Remove trailing semicolon before checking
    body = sql.strip().rstrip(";").strip()
    if ";" in body:
        raise UnsafeSQLError(
            "Multiple SQL statements are not allowed."
        )

    return sql.strip()
