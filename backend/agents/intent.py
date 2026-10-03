"""
Intent Detection Agent
----------------------
Uses the LLM to classify a customer query into one or more of:
    billing, technical, product, complaint, faq

Returns a list of intent strings (1 or 2 intents).
"""
import re

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from agents.llm import get_llm


VALID_INTENTS = ["billing", "technical", "product", "complaint", "faq"]


INTENT_SYSTEM_PROMPT = """You are an intent classification agent for TechMart \
Electronics customer support.

Classify the customer's message into one or more of these categories:

- billing   : payments, subscriptions, invoices, refunds, charges
- technical : login problems, password reset, installation, errors, bugs, device issues
- product   : features, specifications, availability, comparisons, product pricing
- complaint : dissatisfaction, service complaints, escalation requests
- faq       : company policies, general questions, contact info, business hours

RULES:
1. Return ONLY a comma-separated list of categories in lowercase.
2. No explanations. No punctuation other than commas. No extra words.
3. Choose 1 category for simple queries, 2 for mixed queries.
4. Never return more than 2 categories.
5. If nothing fits, return "faq".

EXAMPLES:
- "How do I reset my password?"                     -> technical
- "What is your refund policy?"                     -> billing
- "I paid yesterday but Premium is still locked."   -> billing,technical
- "Your service is terrible, I want to escalate."   -> complaint
- "Do you have a physical office in Europe?"        -> faq
- "How much does the TechMart Pro 14 cost?"         -> product
- "My laptop won't turn on and I want a refund."    -> technical,billing
"""

INTENT_USER_PROMPT = "Customer message: {query}\n\nCategories:"


def detect_intent(query: str) -> list[str]:
    """
    Classify a query into 1-2 valid intents.

    Returns a list like ["billing", "technical"].
    Falls back to ["faq"] if the LLM output is unusable.
    """
    if not query or not query.strip():
        return ["faq"]

    prompt = ChatPromptTemplate.from_messages([
        ("system", INTENT_SYSTEM_PROMPT),
        ("user", INTENT_USER_PROMPT),
    ])

    chain = prompt | get_llm() | StrOutputParser()
    raw = chain.invoke({"query": query}).strip().lower()

    # Clean up LLM output: strip punctuation, split, filter valid
    raw = re.sub(r"[^a-z,\s]", "", raw)
    tokens = [t.strip() for t in raw.split(",") if t.strip()]
    intents = [t for t in tokens if t in VALID_INTENTS]

    # Dedupe while preserving order
    seen = set()
    unique = []
    for i in intents:
        if i not in seen:
            seen.add(i)
            unique.append(i)

    # Cap at 2 intents
    unique = unique[:2]

    return unique if unique else ["faq"]


# ---------- Smoke test ----------
if __name__ == "__main__":
    test_queries = [
        "How do I reset my password?",
        "What is your refund policy?",
        "I paid yesterday but Premium is still locked.",
        "Your service is terrible, I want to escalate.",
        "Do you have a physical office in Europe?",
        "How much does the TechMart Pro 14 cost?",
        "My laptop won't turn on and I want a refund.",
        "Hi",  # edge case: too short
    ]

    print("=" * 70)
    print("Intent Detection Smoke Test")
    print("=" * 70)

    for q in test_queries:
        try:
            intents = detect_intent(q)
            print(f"\nQ: {q}")
            print(f"   -> {intents}")
        except Exception as e:
            print(f"\nQ: {q}")
            print(f"   ERROR: {type(e).__name__}: {e}")