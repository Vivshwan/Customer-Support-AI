"""
User database operations.
Collection: users { _id, email, hashed_password, name, created_at }
"""
import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://127.0.0.1:27017")
DB_NAME = "techmart_support"
COLLECTION = "users"

_client: AsyncIOMotorClient | None = None


def _get_collection():
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    return _client[DB_NAME][COLLECTION]


async def create_user(email: str, hashed_password: str, name: str) -> dict:
    """Insert a new user. Returns the created document (without password)."""
    col = _get_collection()
    doc = {
        "email": email.lower().strip(),
        "hashed_password": hashed_password,
        "name": name.strip(),
        "created_at": datetime.now(timezone.utc),
    }
    result = await col.insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    doc.pop("hashed_password", None)
    return doc


async def get_user_by_email(email: str) -> dict | None:
    """Fetch raw user doc (INCLUDING hashed_password) — for login only."""
    col = _get_collection()
    return await col.find_one({"email": email.lower().strip()})


async def get_user_by_id(user_id: str) -> dict | None:
    """Fetch a user by string id. Strips password."""
    from bson import ObjectId
    try:
        oid = ObjectId(user_id)
    except Exception:
        return None
    col = _get_collection()
    doc = await col.find_one({"_id": oid})
    if doc:
        doc["_id"] = str(doc["_id"])
        doc.pop("hashed_password", None)
    return doc


async def ensure_indexes():
    """Create unique index on email."""
    col = _get_collection()
    await col.create_index("email", unique=True)