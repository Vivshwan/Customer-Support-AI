"""
Agent Router
------------
Detects the intent(s) of a query and dispatches it to the matching
specialized agents. Supports multi-intent queries (up to 2 agents).

Public API:
    route(query) -> dict
"""


from agents.intent import detect_intent
from agents.billing import billing_agent
from agents.technical import technical_agent
from agents.product import product_agent
from agents.complaint import complaint_agent
from agents.faq import faq_agent


# Map intent -> agent callable
AGENT_MAP = {
    "billing":   billing_agent,
    "technical": technical_agent,
    "product":   product_agent,
    "complaint": complaint_agent,
    "faq":       faq_agent,
}


def route(query: str) -> dict:
    """
    Route a customer query to one or more agents.

    Returns:
        {
            "query": str,
            "intents": [str],
            "responses": [ {agent, answer, sources, chunks_used}, ... ],
        }
    """
    if not query or not query.strip():
        return {
            "query": query,
            "intents": [],
            "responses": [],
            "error": "Empty query.",
        }

    intents = detect_intent(query)
    agents_to_run = [AGENT_MAP[i] for i in intents if i in AGENT_MAP]

    if not agents_to_run:
        agents_to_run = [faq_agent]
        intents = ["faq"]

    # Run agents sequentially to avoid Groq free-tier rate limits.
    # (Parallel execution is faster but bursts TPM — re-enable when
    #  you upgrade to a paid tier or move to OpenAI.)
    responses = [agent(query) for agent in agents_to_run] 

    return {
        "query": query,
        "intents": intents,
        "responses": responses,
    }


# ---------- Smoke test ----------
if __name__ == "__main__":
    test_queries = [
        "How do I reset my password?",
        "What is your refund policy?",
        "I paid yesterday but Premium is still locked.",  # ★ multi-agent
        "Your service is terrible, I want to escalate.",
        "How much does the TechMart Pro 14 cost?",
        "My laptop won't turn on and I want a refund.",   # ★ multi-agent
        "What's the capital of France?",                  # refusal case
    ]

    for q in test_queries:
        print("\n" + "=" * 70)
        print(f"Q: {q}")
        print("=" * 70)
        result = route(q)
        print(f"Intents: {result['intents']}")
        print(f"Agents run: {len(result['responses'])}")
        for r in result["responses"]:
            print(f"\n--- [{r['agent'].upper()} AGENT] ---")
            print(r["answer"])
            print(f"  Sources: {r['sources']}")