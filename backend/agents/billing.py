"""Billing Agent — payments, subscriptions, invoices, refunds."""
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from agents.llm import get_llm
from rag.retriever import retrieve_with_sources, format_context


BILLING_SYSTEM_PROMPT = """You are the Billing Agent for TechMart Electronics.

You handle: payments, subscriptions, invoices, refund charges, refund requests.

STRICT RULES:
1. Answer ONLY using the CONTEXT below.
2. If the context lacks the answer, reply exactly:
   "I don't have that information. Let me connect you with a billing specialist."
3. Be precise about amounts, dates, and policy windows.
4. Keep answers to 2-4 sentences.
5. Cite sources as (Source: filename.pdf).

CONTEXT:
{context}
"""


def billing_agent(question: str, context: str | None = None) -> dict:
    if context is None:
        results = retrieve_with_sources(question, k=4)
        context = format_context(results)
        sources = sorted({r["source"] for r in results})
    else:
        sources = []

    prompt = ChatPromptTemplate.from_messages([
        ("system", BILLING_SYSTEM_PROMPT),
        ("user", "Customer question: {question}"),
    ])
    chain = prompt | get_llm() | StrOutputParser()
    answer = chain.invoke({"context": context, "question": question}).strip()

    return {
        "agent": "billing",
        "answer": answer,
        "sources": sources,
        "chunks_used": 0 if context else len(sources),
    }