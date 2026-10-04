"""Complaint Agent — complaints, dissatisfaction, escalation."""
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from agents.llm import get_llm
from rag.retriever import retrieve_with_sources, format_context


COMPLAINT_SYSTEM_PROMPT = """You are the Complaint Agent for TechMart Electronics.

You handle: customer complaints, dissatisfaction, escalation requests.

STRICT RULES:
1. Start with empathy: acknowledge the customer's frustration in one sentence.
2. Answer using ONLY the CONTEXT below.
3. Explain how to file a complaint or request escalation.
4. End every response with:
   "Your case can be escalated to a supervisor via techmart.example/complaints."
5. Cite sources as (Source: filename.pdf).

CONTEXT:
{context}
"""


def complaint_agent(question: str, context: str | None = None) -> dict:
    if context is None:
        results = retrieve_with_sources(question, k=4)
        context = format_context(results)
        sources = sorted({r["source"] for r in results})
    else:
        sources = []

    prompt = ChatPromptTemplate.from_messages([
        ("system", COMPLAINT_SYSTEM_PROMPT),
        ("user", "Customer message: {question}"),
    ])
    chain = prompt | get_llm() | StrOutputParser()
    answer = chain.invoke({"context": context, "question": question}).strip()

    return {
        "agent": "complaint",
        "answer": answer,
        "sources": sources,
        "chunks_used": 0 if context else len(sources),
    }