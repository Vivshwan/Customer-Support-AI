"""
Retriever module
----------------
Loads the saved FAISS index and returns relevant chunks.
Used by all agents for Retrieval-Augmented Generation (RAG).

Quick test (from backend/):
    python -m rag.retriever
"""
from pathlib import Path
from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# ---------- Paths ----------
BACKEND_DIR = Path(__file__).resolve().parent.parent
VECTOR_PATH = BACKEND_DIR / "rag" / "vectorstore" / "faiss_index"

# ---------- Config ----------
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_K = 4


# ---------- Cached loader ----------
@lru_cache(maxsize=1)
def _load_vectorstore() -> FAISS:
    """
    Load and cache the FAISS index.
    Cached so the embedding model loads only once per process.
    """
    if not VECTOR_PATH.exists():
        raise FileNotFoundError(
            f"Vectorstore not found at {VECTOR_PATH}.\n"
            f"Run `python -m rag.ingest` first."
        )

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    return FAISS.load_local(
        str(VECTOR_PATH),
        embeddings,
        allow_dangerous_deserialization=True,  # safe: our own local file
    )


# ---------- Public API ----------
def get_retriever(k: int = DEFAULT_K):
    """Return a LangChain retriever that fetches top-k relevant chunks."""
    db = _load_vectorstore()
    return db.as_retriever(search_kwargs={"k": k})


def retrieve_with_sources(query: str, k: int = DEFAULT_K) -> list[dict]:
    """
    Retrieve top-k chunks with source metadata.
    Useful for citations in the frontend and for feeding agents.

    Returns a list of dicts:
        {
            "content": str,
            "source":  str,   # e.g. "RefundPolicy.pdf"
            "page":    int | None,
            "score":   float  # lower = more similar (L2 distance)
        }
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
    Each chunk is prefixed with its source so the LLM can cite it.
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