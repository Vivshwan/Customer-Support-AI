"""
TechMart Multi-Agent Customer Support — FastAPI backend.

Endpoints:
    GET  /              → health check
    GET  /health        → deep health (Mongo + vectorstore)
    POST /chat          → main chat endpoint (routes query to agents)
    GET  /history/{sid} → fetch conversation history
    DELETE /history/{sid} → clear history
"""
import uuid
from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agents.router import route
from database import memory

load_dotenv()


# ---------- App ----------
app = FastAPI(
    title="TechMart Multi-Agent Customer Support AI",
    description="Multi-agent RAG-powered customer support backend.",
    version="0.1.0",
)

# CORS — allow Vite dev server (5173) and common origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Schemas ----------
class ChatRequest(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    message: str = Field(..., min_length=1, max_length=2000)


class AgentResponse(BaseModel):
    agent: str
    answer: str
    sources: list[str] = []


class ChatResponse(BaseModel):
    session_id: str
    query: str
    intents: list[str]
    responses: list[AgentResponse]
    timestamp: str


# ---------- Routes ----------
@app.get("/")
def root():
    return {"status": "ok", "service": "techmart-support-ai"}


@app.get("/health")
async def health():
    mongo_ok = await memory.ping()
    return {
        "status": "healthy" if mongo_ok else "degraded",
        "mongodb": "up" if mongo_ok else "down",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """
    Main chat endpoint. Routes the query to one or more agents,
    saves both messages to MongoDB, and returns the combined response.
    """
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Empty message.")

    # 1. Persist user message
    try:
        await memory.save_user_message(req.session_id, req.message)
    except Exception as e:
        # Non-fatal — continue even if DB write fails
        print(f"[WARN] Failed to save user message: {e}")

    # 2. Route to agents
    try:
        result = route(req.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {e}")

    # 3. Combine answers into a single assistant message for storage
    combined_answer = "\n\n".join(
        f"[{r['agent'].upper()}]\n{r['answer']}" for r in result["responses"]
    )
    all_sources = sorted({s for r in result["responses"] for s in r.get("sources", [])})

    # 4. Persist assistant message
    try:
        await memory.save_assistant_message(
            req.session_id,
            combined_answer,
            intents=result["intents"],
            sources=all_sources,
        )
    except Exception as e:
        print(f"[WARN] Failed to save assistant message: {e}")

    return ChatResponse(
        session_id=req.session_id,
        query=req.message,
        intents=result["intents"],
        responses=[
            AgentResponse(
                agent=r["agent"],
                answer=r["answer"],
                sources=r.get("sources", []),
            )
            for r in result["responses"]
        ],
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@app.get("/history/{session_id}")
async def history(session_id: str, limit: int = 20):
    """Fetch the last N messages for a session, oldest first."""
    rows = await memory.get_history(session_id, limit=limit)
    return {"session_id": session_id, "count": len(rows), "messages": rows}


@app.delete("/history/{session_id}")
async def clear(session_id: str):
    """Clear all messages for a session."""
    count = await memory.clear_history(session_id)
    return {"session_id": session_id, "deleted": count}