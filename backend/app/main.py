"""
FastAPI Application — AI Data Insights Dashboard Backend

Start with:
    cd backend
    uvicorn app.main:app --reload --port 8000
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.query_router import router as query_router
from .database.db import engine
from .database.models import Base

# Create application tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Data Insights Dashboard",
    description="Ask natural language questions about your business data",
    version="1.0.0",
)

# CORS — allow any origin for easy deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes
app.include_router(query_router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "AI Data Insights Dashboard API is running"}
