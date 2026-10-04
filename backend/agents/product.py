"""Product Agent — features, specs, availability, comparisons, product pricing."""
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from agents.llm import get_llm
from rag.retriever import retrieve_with_sources, format_context


PRODUCT_SYSTEM_PROMPT = """You are the Product Agent for TechMart Electronics.

You handle: product features, specifications, availability, comparisons, product pricing.

STRICT RULES:
1. Answer ONLY using the CONTEXT below.
2. Give prices exactly as written (do not approximate).
3. When comparing products, use a short bullet list.
4. If the context lacks the answer, reply exactly:
   "I don't have that information. Let me connect you with a product specialist."
5. Cite sources as (Source: filename.pdf).

CONTEXT:
{context}
"""


def product_agent(question: str, context: str | None = None) -> dict:
    if context is None:
        results = retrieve_with_sources(question, k=4)
        context = format_context(results)
        sources = sorted({r["source"] for r in results})
    else:
        sources = []

    prompt = ChatPromptTemplate.from_messages([
        ("system", PRODUCT_SYSTEM_PROMPT),
        ("user", "Customer question: {question}"),
    ])
    chain = prompt | get_llm() | StrOutputParser()
    answer = chain.invoke({"context": context, "question": question}).strip()

    return {
        "agent": "product",
        "answer": answer,
        "sources": sources,
        "chunks_used": 0 if context else len(sources),
    }