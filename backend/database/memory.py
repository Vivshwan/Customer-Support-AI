"""
Conversation memory — MongoDB-backed chat history.
Scoped per user.

Collections:
    conversations: { _id, user_id, title, created_at, updated_at }
    messages:      { conversation_id, user_id, role, content, ... }

Public API:
    create_conversation(user_id, title) -> dict
    list_conversations(user_id) -> list
    get_conversation(conv_id, user_id) -> dict | None
    delete_conversation(conv_id, user_id) -> int
    save_user_message(conv_id, user_id, content)
    save_assistant_message(conv_id, user_id, content, intents, sources)
    get_history(conv_id, user_id, limit)
"""
import os
from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://127.0.0.1:27017")
DB_NAME = "techmart_support"

_client: AsyncIOMotorClient | None = None


def _db():
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    return _client[DB_NAME]


def _messages():
    return _db()["messages"]


def _conversations():
    return _db()["conversations"]


# ---------- Conversations ----------
async def create_conversation(user_id: str, title: str = "New chat") -> dict:
    col = _conversations()
    now = datetime.now(timezone.utc)
    doc = {
        "user_id": user_id,
        "title": title.strip()[:80] or "New chat",
        "created_at": now,
        "updated_at": now,
    }
    result = await col.insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    return doc


async def list_conversations(user_id: str, limit: int = 50) -> list[dict]:
    col = _conversations()
    cursor = col.find({"user_id": user_id}).sort("updated_at", -1).limit(limit)
    rows = await cursor.to_list(length=limit)
    for r in rows:
        r["_id"] = str(r["_id"])
        for k in ("created_at", "updated_at"):
            if isinstance(r.get(k), datetime):
                r[k] = r[k].isoformat()
    return rows


async def get_conversation(conv_id: str, user_id: str) -> dict | None:
    try:
        oid = ObjectId(conv_id)
    except Exception:
        return None
    doc = await _conversations().find_one({"_id": oid, "user_id": user_id})
    if doc:
        doc["_id"] = str(doc["_id"])
        for k in ("created_at", "updated_at"):
            if isinstance(doc.get(k), datetime):
                doc[k] = doc[k].isoformat()
    return doc


async def delete_conversation(conv_id: str, user_id: str) -> int:
    try:
        oid = ObjectId(conv_id)
    except Exception:
        return 0
    # Verify ownership
    conv = await _conversations().find_one({"_id": oid, "user_id": user_id})
    if not conv:
        return 0
    await _conversations().delete_one({"_id": oid})
    result = await _messages().delete_many({"conversation_id": conv_id})
    return result.deleted_count


async def touch_conversation(conv_id: str) -> None:
    """Update the conversation's updated_at timestamp."""
    try:
        oid = ObjectId(conv_id)
    except Exception:
        return
    await _conversations().update_one(
        {"_id": oid},
        {"$set": {"updated_at": datetime.now(timezone.utc)}},
    )


# ---------- Messages ----------
async def save_user_message(conv_id: str, user_id: str, content: str) -> None:
    await _messages().insert_one({
        "conversation_id": conv_id,
        "user_id": user_id,
        "role": "user",
        "content": content,
        "timestamp": datetime.now(timezone.utc),
    })
    await touch_conversation(conv_id)


async def save_assistant_message(
    conv_id: str,
    user_id: str,
    content: str,
    intents: list[str] | None = None,
    sources: list[str] | None = None,
) -> None:
    await _messages().insert_one({
        "conversation_id": conv_id,
        "user_id": user_id,
        "role": "assistant",
        "content": content,
        "intents": intents or [],
        "sources": sources or [],
        "timestamp": datetime.now(timezone.utc),
    })
    await touch_conversation(conv_id)


async def get_history(conv_id: str, user_id: str, limit: int = 50) -> list[dict[str, Any]]:
    # Verify the conversation belongs to this user
    conv = await get_conversation(conv_id, user_id)
    if not conv:
        return []

    cursor = _messages().find({"conversation_id": conv_id}).sort("timestamp", 1).limit(limit)
    rows = await cursor.to_list(length=limit)
    for r in rows:
        r["_id"] = str(r["_id"])
        if isinstance(r.get("timestamp"), datetime):
            r["timestamp"] = r["timestamp"].isoformat()
    return rows


async def ping() -> bool:
    try:
        await _db().command("ping")
        return True
    except Exception:
        return False