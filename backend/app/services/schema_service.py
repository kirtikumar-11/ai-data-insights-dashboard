"""
Schema discovery service.
Queries PostgreSQL information_schema to build a structured description
of all tables and columns for injection into LLM prompts.
"""
from sqlalchemy import text


def get_schema_description(engine) -> str:
    """
    Reads all public tables/columns from PostgreSQL and returns a
    formatted string suitable for LLM prompt injection.
    """
    query = text("""
        SELECT table_name, column_name, data_type, is_nullable,
               column_default
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name NOT IN ('query_logs')
        ORDER BY table_name, ordinal_position;
    """)

    with engine.connect() as conn:
        rows = conn.execute(query).fetchall()

    if not rows:
        return "No tables found in the database."

    # Group columns by table
    tables: dict[str, list[str]] = {}
    for row in rows:
        table_name = row[0]
        col_name = row[1]
        data_type = row[2]
        nullable = "NULL" if row[3] == "YES" else "NOT NULL"
        if table_name not in tables:
            tables[table_name] = []
        tables[table_name].append(f"  - {col_name} ({data_type}, {nullable})")

    # Build the relationships description from known FK patterns
    relationships = _get_relationships(engine)

    # Format output
    lines = ["DATABASE SCHEMA:\n"]
    for table_name, cols in tables.items():
        lines.append(f"Table: {table_name}")
        lines.extend(cols)
        lines.append("")

    if relationships:
        lines.append("RELATIONSHIPS:")
        lines.extend(relationships)

    return "\n".join(lines)


def _get_relationships(engine) -> list[str]:
    """Read foreign key relationships from PostgreSQL system catalog."""
    query = text("""
        SELECT
            tc.table_name AS source_table,
            kcu.column_name AS source_column,
            ccu.table_name AS target_table,
            ccu.column_name AS target_column
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage AS ccu
            ON tc.constraint_name = ccu.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY'
        ORDER BY tc.table_name;
    """)

    with engine.connect() as conn:
        rows = conn.execute(query).fetchall()

    return [
        f"  {row[0]}.{row[1]} -> {row[2]}.{row[3]}"
        for row in rows
    ]
