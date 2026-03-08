"""
LLM Service — Converts natural language questions into SQL using the Gemini API.
"""
import os
import re
from google import genai
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def generate_sql(question: str, schema: str) -> str:
    """
    Send the user's natural language question along with the database schema
    to the LLM and return a clean SQL query.
    """
    prompt = f"""You are a PostgreSQL expert. Your job is to convert a user's natural language question into a valid PostgreSQL SELECT query.

DATABASE SCHEMA:
{schema}

RULES:
- Return ONLY the SQL query, no explanations, no markdown formatting.
- Use only SELECT statements. Never use DELETE, UPDATE, DROP, ALTER, INSERT, or TRUNCATE.
- Always use proper table and column names from the schema above.
- Use JOINs when the question involves data from multiple tables.
- Use aggregations (SUM, COUNT, AVG, etc.) when appropriate.
- ONLY use standard PostgreSQL functions. NEVER use SQLite functions like 'strftime' (use 'to_char' instead).
- Add ORDER BY and LIMIT when the question asks for "top", "best", "highest", etc.
- If the question is ambiguous, make a reasonable assumption and proceed.
- For monetary values, use the 'price' column from order_items or 'payment_value' from order_payments.
- The 'products' table has a 'product_category' column with English category names.
- Ensure the query is complete, well-formed, and contains a FROM clause.

USER QUESTION:
{question}

SQL QUERY:"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config={
            "temperature": 0.1,
            "max_output_tokens": 2048,
        }
    )

    raw_sql = response.text.strip()
    return _clean_sql(raw_sql)


def generate_insight(question: str, data_summary: str) -> str:
    """
    Given the user's question and a summary of the query results,
    generate a short business insight.
    """
    prompt = f"""You are a business data analyst. Based on the user's question and the query results below, provide:
1. A direct, concise answer to the question (1-2 sentences).
2. A short business insight or observation focusing on the "why" or actionable takeaway (1-2 sentences).

USER QUESTION: {question}

QUERY RESULTS:
{data_summary}

Respond in this exact format:
ANSWER: <your direct answer>
INSIGHT: <your business insight>"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config={
            "temperature": 0.3,
            "max_output_tokens": 300,
        }
    )

    return response.text.strip()


def _clean_sql(raw: str) -> str:
    """Strip markdown code fences and extra whitespace from LLM output."""
    # Remove ```sql ... ``` wrappers
    cleaned = re.sub(r"^```(?:sql)?\s*", "", raw, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    cleaned = cleaned.strip().rstrip(";") + ";"
    return cleaned
