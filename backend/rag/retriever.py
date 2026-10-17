"""
Retriever module (Gemini API Mode)
----------------------------------
Loads the saved FAISS index and returns relevant chunks.
Uses Google Gemini API for embeddings to save memory on cloud deployments.

Quick test (from backend/):
    python -m rag.retriever
"""
import os
from pathlib import Path
from functools import lru_cache

from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

# ---------- Paths ----------
BACKEND_DIR = Path(__file__).resolve().parent.parent
VECTOR_PATH = BACKEND_DIR / "rag" / "vectorstore" / "faiss_index"

# ---------- Config ----------
EMBEDDING_MODEL = "gemini-embedding-001"
DEFAULT_K = 4


# ---------- Cached loader ----------
@lru_cache(maxsize=1)
def _load_vectorstore() -> FAISS:
    """
    Load and cache the FAISS index.
    Uses the Gemini API for query embeddings.
    """
    if not VECTOR_PATH.exists():
        raise FileNotFoundError(
            f"Vectorstore not found at {VECTOR_PATH}.\n"
            f"Run `python -m rag.ingest` first."
        )

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY is missing in backend/.env")

    embeddings = GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL,
        google_api_key=api_key
    )

    return FAISS.load_local(
        str(VECTOR_PATH),
        embeddings,
        allow_dangerous_deserialization=True,
    )


# ---------- Public API ----------
def get_retriever(k: int = DEFAULT_K):
    """Return a LangChain retriever that fetches top-k relevant chunks."""
    db = _load_vectorstore()
    return db.as_retriever(search_kwargs={"k": k})


def retrieve_with_sources(query: str, k: int = DEFAULT_K) -> list[dict]:
    """
    Retrieve top-k chunks with source metadata.
    """
    db = _load_vectorstore()
    results = db.similarity_search_with_score(query, k=k)

    return [
        {
            "content": doc.page_content,
            "source": doc.metadata.get("source_file", "unknown"),
            "page": doc.metadata.get("page", None),
            "score": float(score),
        }
        for doc, score in results
    ]


def format_context(results: list[dict]) -> str:
    """
    Format retrieved chunks into a clean context string for the LLM.
    """
    if not results:
        return "(No relevant context found in the knowledge base.)"

    parts = []
    for i, r in enumerate(results, start=1):
        header = f"[Source {i}: {r['source']}]"
        parts.append(f"{header}\n{r['content']}")
    return "\n\n---\n\n".join(parts)


# ---------- Smoke test ----------
if __name__ == "__main__":
    test_queries = [
        "What is the refund policy?",
        "How long does shipping take?",
        "I paid for Premium but it's still locked",
    ]

    for q in test_queries:
        print(f"\n>> Query: {q}")
        results = retrieve_with_sources(q, k=2)
        for r in results:
            preview = r["content"][:180].replace("\n", " ").strip()
            print(f"   [{r['source']}] (score={r['score']:.3f})")
            print(f"   {preview}...")