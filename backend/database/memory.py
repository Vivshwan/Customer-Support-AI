"""
Conversation memory — MongoDB-backed chat history.

Collections:
    messages: { session_id, role, content, timestamp, intents?, sources? }

Public API:
    save_user_message(session_id, content)
    save_assistant_message(session_id, content, intents, sources)
    get_history(session_id, limit=20)
    clear_history(session_id)
"""
import os
from datetime import datetime, timezone
from typing import Any

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = "techmart_support"
COLLECTION = "messages"

# Single shared client (Motor is async, safe to reuse)
_client: AsyncIOMotorClient | None = None


def _get_collection():
    """Lazy-init the Mongo client + collection."""
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    return _client[DB_NAME][COLLECTION]


# ---------- Writes ----------
async def save_user_message(session_id: str, content: str) -> None:
    col = _get_collection()
    await col.insert_one({
        "session_id": session_id,
        "role": "user",
        "content": content,
        "timestamp": datetime.now(timezone.utc),
    })


async def save_assistant_message(
    session_id: str,
    content: str,
    intents: list[str] | None = None,
    sources: list[str] | None = None,
) -> None:
    col = _get_collection()
    await col.insert_one({
        "session_id": session_id,
        "role": "assistant",
        "content": content,
        "intents": intents or [],
        "sources": sources or [],
        "timestamp": datetime.now(timezone.utc),
    })


# ---------- Reads ----------
async def get_history(session_id: str, limit: int = 20) -> list[dict[str, Any]]:
    """
    Return the most recent `limit` messages for a session,
    ordered chronologically (oldest first).
    """
    col = _get_collection()
    cursor = col.find({"session_id": session_id}).sort("timestamp", -1).limit(limit)
    rows = await cursor.to_list(length=limit)

    # Reverse so oldest comes first, and convert _id/ObjectId to str
    rows.reverse()
    for r in rows:
        r["_id"] = str(r["_id"])
        if isinstance(r.get("timestamp"), datetime):
            r["timestamp"] = r["timestamp"].isoformat()
    return rows


async def clear_history(session_id: str) -> int:
    """Delete all messages for a session. Returns deleted count."""
    col = _get_collection()
    result = await col.delete_many({"session_id": session_id})
    return result.deleted_count


# ---------- Health ----------
async def ping() -> bool:
    """Check MongoDB is reachable."""
    try:
        await _get_collection().database.command("ping")
        return True
    except Exception:
        return False