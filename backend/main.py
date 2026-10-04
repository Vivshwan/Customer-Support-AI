"""
TechMart Multi-Agent Customer Support — FastAPI backend.

Endpoints:
    GET  /                      health check
    GET  /health                deep health
    POST /auth/register         create user
    POST /auth/login            get JWT
    GET  /auth/me               current user profile

    POST /chat                  send message (auth required)
    GET  /conversations         list user's conversations
    POST /conversations         create new conversation
    GET  /conversations/{id}    get conversation + history
    DELETE /conversations/{id}  delete conversation
"""
from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agents.router import route
from auth.dependencies import get_current_user
from auth.routes import router as auth_router
from database import memory, users

load_dotenv()


# ---------- App ----------
app = FastAPI(
    title="TechMart Multi-Agent Customer Support AI",
    description="Multi-agent RAG-powered customer support backend.",
    version="0.2.0",
)

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

# Include auth routes
app.include_router(auth_router)


# ---------- Startup ----------
@app.on_event("startup")
async def startup():
    await users.ensure_indexes()


# ---------- Schemas ----------
class ChatRequest(BaseModel):
    conversation_id: str
    message: str = Field(..., min_length=1, max_length=2000)


class AgentResponse(BaseModel):
    agent: str
    answer: str
    sources: list[str] = []


class ChatResponse(BaseModel):
    conversation_id: str
    query: str
    intents: list[str]
    responses: list[AgentResponse]
    timestamp: str


class NewConversationRequest(BaseModel):
    title: str = "New chat"


# ---------- Health ----------
@app.get("/")
def root():
    return {"status": "ok", "service": "techmart-support-ai", "version": "0.2.0"}


@app.get("/health")
async def health():
    mongo_ok = await memory.ping()
    return {
        "status": "healthy" if mongo_ok else "degraded",
        "mongodb": "up" if mongo_ok else "down",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ---------- Conversations ----------
@app.post("/conversations")
async def create_conversation(
    req: NewConversationRequest,
    current_user: dict = Depends(get_current_user),
):
    conv = await memory.create_conversation(current_user["_id"], req.title)
    return conv


@app.get("/conversations")
async def list_conversations(
    current_user: dict = Depends(get_current_user),
):
    rows = await memory.list_conversations(current_user["_id"])
    return {"count": len(rows), "conversations": rows}


@app.get("/conversations/{conv_id}")
async def get_conversation(
    conv_id: str,
    current_user: dict = Depends(get_current_user),
):
    conv = await memory.get_conversation(conv_id, current_user["_id"])
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    messages = await memory.get_history(conv_id, current_user["_id"])
    return {"conversation": conv, "messages": messages}


@app.delete("/conversations/{conv_id}")
async def delete_conversation(
    conv_id: str,
    current_user: dict = Depends(get_current_user),
):
    deleted = await memory.delete_conversation(conv_id, current_user["_id"])
    return {"deleted_messages": deleted}


# ---------- Chat ----------
@app.post("/chat", response_model=ChatResponse)
async def chat(
    req: ChatRequest,
    current_user: dict = Depends(get_current_user),
):
    """Send a message; route to agents; persist; return combined response."""
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Empty message.")

    # Verify the conversation belongs to this user
    conv = await memory.get_conversation(req.conversation_id, current_user["_id"])
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    # Save user message
    await memory.save_user_message(
        req.conversation_id, current_user["_id"], req.message
    )

    # Route to agents
    try:
        result = route(req.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {e}")

    combined = "\n\n".join(
        f"[{r['agent'].upper()}]\n{r['answer']}" for r in result["responses"]
    )
    all_sources = sorted(
        {s for r in result["responses"] for s in r.get("sources", [])}
    )

    # Save assistant message
    await memory.save_assistant_message(
        req.conversation_id,
        current_user["_id"],
        combined,
        intents=result["intents"],
        sources=all_sources,
    )

    # Auto-title new conversations from first user message
    if conv["title"] == "New chat":
        new_title = req.message.strip()[:60] or "New chat"
        try:
            from bson import ObjectId
            from database.memory import _conversations
            await _conversations().update_one(
                {"_id": ObjectId(req.conversation_id)},
                {"$set": {"title": new_title}},
            )
        except Exception:
            pass

    return ChatResponse(
        conversation_id=req.conversation_id,
        query=req.message,
        intents=result["intents"],
        responses=[
            AgentResponse(
                agent=r["agent"], answer=r["answer"], sources=r.get("sources", [])
            )
            for r in result["responses"]
        ],
        timestamp=datetime.now(timezone.utc).isoformat(),
    )