"""
FAQ Agent
---------
Answers general questions, company policies, and contact info
using the RAG pipeline + GPT-4o-mini.
"""
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from agents.llm import get_llm
from rag.retriever import retrieve_with_sources, format_context


FAQ_SYSTEM_PROMPT = """You are the FAQ Agent for TechMart Electronics, a consumer \
electronics company. You handle general customer questions about company policies, \
contact information, business hours, and account FAQs.

STRICT RULES:
1. Answer ONLY using the CONTEXT provided below.
2. If the context does not contain the answer, reply exactly:
   "I don't have that information in my knowledge base. Let me connect you with a human agent."
3. Do NOT invent policies, prices, or facts.
4. Keep answers concise (2-4 sentences).
5. If the context includes a specific number, date, or policy window, use it exactly.
6. At the end, cite sources in this format: (Source: filename.pdf)

CONTEXT:
{context}
"""

FAQ_USER_PROMPT = "Customer question: {question}"


def faq_agent(question: str, k: int = 4) -> dict:
    """
    Run the FAQ agent on a question.

    Returns:
        {
            "agent": "faq",
            "answer": str,
            "sources": [list of source filenames],
            "chunks_used": int
        }
    """
    # 1. Retrieve relevant chunks
    results = retrieve_with_sources(question, k=k)
    context = format_context(results)
    sources = sorted({r["source"] for r in results})

    # 2. Build the prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", FAQ_SYSTEM_PROMPT),
        ("user", FAQ_USER_PROMPT),
    ])

    # 3. Call LLM
    chain = prompt | get_llm() | StrOutputParser()
    answer = chain.invoke({"context": context, "question": question})

    return {
        "agent": "faq",
        "answer": answer.strip(),
        "sources": sources,
        "chunks_used": len(results),
    }


# ---------- Smoke test ----------
if __name__ == "__main__":
    test_questions = [
        "What is your refund policy?",
        "How long does shipping take?",
        "Do you have a physical office in Europe?",
        "What's the capital of France?",  # should refuse — out of scope
    ]

    for q in test_questions:
        print("\n" + "=" * 60)
        print(f"Q: {q}")
        print("=" * 60)
        try:
            result = faq_agent(q)
            print(f"A: {result['answer']}")
            print(f"\nSources: {result['sources']}")
            print(f"Chunks used: {result['chunks_used']}")
        except Exception as e:
            print(f"ERROR: {type(e).__name__}: {e}")
            
def faq_agent(question: str, context: str | None = None) -> dict:
    """
    Run the FAQ agent.

    Args:
        question: customer question
        context:  optional pre-retrieved context. If None, retrieves fresh.

    Returns:
        { "agent", "answer", "sources", "chunks_used" }
    """
    if context is None:
        results = retrieve_with_sources(question, k=4)
        context = format_context(results)
        sources = sorted({r["source"] for r in results})
        chunks_used = len(results)
    else:
        results = []  # context provided externally
        sources = []
        chunks_used = 0

    prompt = ChatPromptTemplate.from_messages([
        ("system", FAQ_SYSTEM_PROMPT),
        ("user", FAQ_USER_PROMPT),
    ])
    chain = prompt | get_llm() | StrOutputParser()
    answer = chain.invoke({"context": context, "question": question})

    return {
        "agent": "faq",
        "answer": answer.strip(),
        "sources": sources,
        "chunks_used": chunks_used,
    }