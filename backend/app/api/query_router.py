"""
Query Router — Orchestrates the full pipeline:
  Question → Schema → LLM SQL → Validate → Execute → Chart → Insight → Log → Response
"""
import time
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from ..database.db import engine, get_db
from ..services.schema_service import get_schema_description
from ..services.llm_service import generate_sql, generate_insight
from ..services.sql_validator import validate_sql, UnsafeSQLError
from ..services.chart_service import generate_chart_config
from ..services.insight_service import build_data_summary
from ..utils.query_logger import log_query, get_recent_queries

router = APIRouter()


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------
class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    question: str
    answer: str
    insight: str
    generated_sql: str
    chart: dict[str, Any]
    execution_time: float
    result_rows: int


class HistoryItem(BaseModel):
    id: int
    question: str
    generated_sql: str | None
    execution_time: float | None
    result_rows: int | None
    status: str
    timestamp: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@router.post("/query", response_model=QueryResponse)
async def handle_query(req: QueryRequest, db: Session = Depends(get_db)):
    """
    Main endpoint — takes a natural language question and returns
    an answer, chart config, and insight.
    """
    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    start = time.time()

    try:
        # 1. Get database schema
        schema = get_schema_description(engine)

        # 2. Generate SQL from question
        sql = generate_sql(question, schema)

        # 3. Validate SQL safety
        sql = validate_sql(sql)

        # 4. Execute query
        with engine.connect() as conn:
            result = conn.execute(text(sql))
            columns = list(result.keys())
            rows = [dict(zip(columns, row)) for row in result.fetchall()]

        elapsed = round(time.time() - start, 3)

        # 5. Generate chart config
        chart = generate_chart_config(columns, rows)

        # 6. Generate insight
        data_summary = build_data_summary(columns, rows)
        insight_response = generate_insight(question, data_summary)

        # Parse answer and insight from LLM response
        answer, insight = _parse_insight_response(insight_response)

        # 7. Log query
        log_query(
            db=db,
            question=question,
            generated_sql=sql,
            execution_time=elapsed,
            result_rows=len(rows),
            status="success",
        )

        return QueryResponse(
            question=question,
            answer=answer,
            insight=insight,
            generated_sql=sql,
            chart=chart,
            execution_time=elapsed,
            result_rows=len(rows),
        )

    except UnsafeSQLError as e:
        elapsed = round(time.time() - start, 3)
        log_query(
            db=db,
            question=question,
            generated_sql=None,
            execution_time=elapsed,
            result_rows=0,
            status="error",
            error_message=str(e),
        )
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        import traceback
        traceback.print_exc()
        
        elapsed = round(time.time() - start, 3)
        log_query(
            db=db,
            question=question,
            generated_sql=locals().get("sql"),
            execution_time=elapsed,
            result_rows=0,
            status="error",
            error_message=str(e),
        )
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@router.get("/history", response_model=list[HistoryItem])
async def get_history(limit: int = 20, db: Session = Depends(get_db)):
    """Return recent query history."""
    entries = get_recent_queries(db, limit=limit)
    return [
        HistoryItem(
            id=e.id,
            question=e.question,
            generated_sql=e.generated_sql,
            execution_time=e.execution_time,
            result_rows=e.result_rows,
            status=e.status,
            timestamp=e.timestamp.isoformat() if e.timestamp else "",
        )
        for e in entries
    ]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _parse_insight_response(response: str) -> tuple[str, str]:
    """Parse the ANSWER: ... INSIGHT: ... format from the LLM, supporting multi-line strings."""
    answer_parts = []
    insight_parts = []
    current_mode = None

    for line in response.split("\n"):
        clean_line = line.strip()
        if clean_line.upper().startswith("ANSWER:"):
            current_mode = "answer"
            answer_parts.append(clean_line[len("ANSWER:"):].strip())
        elif clean_line.upper().startswith("INSIGHT:"):
            current_mode = "insight"
            insight_parts.append(clean_line[len("INSIGHT:"):].strip())
        elif current_mode == "answer" and clean_line:
            answer_parts.append(clean_line)
        elif current_mode == "insight" and clean_line:
            insight_parts.append(clean_line)

    answer = " ".join(answer_parts).strip()
    insight = " ".join(insight_parts).strip()

    # Fallback if format wasn't followed
    if not answer and not insight:
        answer = response.strip()
        insight = ""

    return answer, insight
