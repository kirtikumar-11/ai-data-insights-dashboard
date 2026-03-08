"""
Query Logger — Records every query to the query_logs table for auditing and history.
"""
from sqlalchemy.orm import Session
from ..database.models import QueryLog


def log_query(
    db: Session,
    question: str,
    generated_sql: str | None = None,
    execution_time: float | None = None,
    result_rows: int | None = None,
    status: str = "success",
    error_message: str | None = None,
) -> QueryLog:
    """Insert a record into query_logs and return it."""
    entry = QueryLog(
        question=question,
        generated_sql=generated_sql,
        execution_time=execution_time,
        result_rows=result_rows,
        status=status,
        error_message=error_message,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def get_recent_queries(db: Session, limit: int = 20) -> list[QueryLog]:
    """Return the most recent query log entries."""
    return (
        db.query(QueryLog)
        .order_by(QueryLog.timestamp.desc())
        .limit(limit)
        .all()
    )
