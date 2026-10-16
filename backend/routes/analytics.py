"""
Analytics routes — compute usage stats from MongoDB.
All endpoints require authentication; stats are scoped per user.
"""
from datetime import datetime, timedelta, timezone
from collections import Counter

from fastapi import APIRouter, Depends

from auth.dependencies import get_current_user
from database.memory import _conversations, _messages

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary")
async def summary(current_user: dict = Depends(get_current_user)):
    """
    Return aggregated usage stats for the current user:
      - totals: conversations, messages, agent calls
      - agents: usage count per agent type
      - daily: last 7 days message counts
      - recent: 5 most recent conversations
    """
    user_id = current_user["_id"]

    # ---------- Totals ----------
    total_conversations = await _conversations().count_documents(
        {"user_id": user_id}
    )
    total_messages = await _messages().count_documents({"user_id": user_id})
    assistant_messages = await _messages().count_documents(
        {"user_id": user_id, "role": "assistant"}
    )

    # ---------- Agent usage ----------
    agent_counter: Counter[str] = Counter()
    cursor = _messages().find(
        {"user_id": user_id, "role": "assistant"},
        {"intents": 1},
    )
    async for doc in cursor:
        for intent in doc.get("intents", []) or []:
            agent_counter[intent] += 1

    # Ensure all 5 agent types always show up
    for agent in ["billing", "technical", "product", "complaint", "faq"]:
        agent_counter.setdefault(agent, 0)

    # ---------- Daily messages (last 7 days) ----------
    now = datetime.now(timezone.utc)
    seven_days_ago = now - timedelta(days=7)
    daily_counts: dict[str, int] = {}

    # Pre-fill last 7 days with 0
    for i in range(7):
        day = (now - timedelta(days=6 - i)).strftime("%Y-%m-%d")
        daily_counts[day] = 0

    cursor = _messages().find(
        {
            "user_id": user_id,
            "timestamp": {"$gte": seven_days_ago},
        },
        {"timestamp": 1},
    )
    async for doc in cursor:
        ts = doc.get("timestamp")
        if isinstance(ts, datetime):
            day = ts.strftime("%Y-%m-%d")
            if day in daily_counts:
                daily_counts[day] += 1

    daily = [{"date": d, "count": c} for d, c in daily_counts.items()]

    # ---------- Recent conversations ----------
    cursor = _conversations().find({"user_id": user_id}).sort(
        "updated_at", -1
    ).limit(5)
    recent = []
    async for doc in cursor:
        msg_count = await _messages().count_documents(
            {"conversation_id": str(doc["_id"])}
        )
        recent.append({
            "id": str(doc["_id"]),
            "title": doc.get("title", "Untitled"),
            "message_count": msg_count,
            "updated_at": doc["updated_at"].isoformat()
            if isinstance(doc.get("updated_at"), datetime)
            else str(doc.get("updated_at", "")),
        })

    return {
        "totals": {
            "conversations": total_conversations,
            "messages": total_messages,
            "assistant_messages": assistant_messages,
            "agent_calls": sum(agent_counter.values()),
        },
        "agents": [
            {"agent": a, "count": c}
            for a, c in sorted(agent_counter.items(), key=lambda x: -x[1])
        ],
        "daily": daily,
        "recent": recent,
    }