# AI Data Insights Dashboard

A full-stack, AI-powered natural language analytics dashboard.

## Tech Stack
- **Frontend**: Next.js, React, ECharts
- **Backend**: FastAPI, PostgreSQL, SQLAlchemy
- **AI**: Gemini API (`gemini-2.5-flash`) via `google-genai` SDK

## Running the Project
1. **Backend**: `cd backend && python -m uvicorn app.main:app --reload --port 8000`
2. **Frontend**: `cd frontend && npm run dev`
3. **Database**: Requires PostgreSQL running on port 5432 with the `ai_dashboard` database.

*(Note: The CSV data has already been loaded into the database via `data_pipeline.py`)*
