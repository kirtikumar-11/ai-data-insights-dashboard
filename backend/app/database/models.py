"""
SQLAlchemy models for application-specific tables (e.g., query logging).
The e-commerce data tables are created by the data pipeline, not here.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from .db import Base


class QueryLog(Base):
    """Stores every user query and the generated SQL for auditing and history."""
    __tablename__ = "query_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    question = Column(Text, nullable=False)
    generated_sql = Column(Text, nullable=True)
    execution_time = Column(Float, nullable=True)          # seconds
    result_rows = Column(Integer, nullable=True)
    status = Column(String(20), default="success")         # success | error
    error_message = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
