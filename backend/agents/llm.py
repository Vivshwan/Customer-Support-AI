"""
Shared LLM factory with automatic rate-limit retry.
Reads LLM_PROVIDER from .env and returns the matching chat model.
"""
import os
import time
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()

DEFAULT_PROVIDER = "groq"


@lru_cache(maxsize=1)
def get_llm():
    """Return a cached chat model based on LLM_PROVIDER."""
    provider = os.getenv("LLM_PROVIDER", DEFAULT_PROVIDER).strip().lower()

    if provider == "groq":
        return _build_groq()
    elif provider == "openai":
        return _build_openai()
    else:
        raise ValueError(
            f"Unknown LLM_PROVIDER='{provider}'. Use 'groq' or 'openai'."
        )


def _build_groq():
    from langchain_groq import ChatGroq

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is missing in backend/.env")

    return ChatGroq(
        model="openai/gpt-oss-20b",       # 👈 lighter model = higher rate limit headroom
        temperature=0.2,
        api_key=api_key,
        max_tokens=600,
        max_retries=5,                     # 👈 built-in retry on 429/5xx
        timeout=60,
    )


def _build_openai():
    from langchain_openai import ChatOpenAI

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing in backend/.env")

    return ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.2,
        api_key=api_key,
        max_tokens=600,
        max_retries=3,
        timeout=60,
    )