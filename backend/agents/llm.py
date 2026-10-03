"""
Shared LLM factory.
Reads LLM_PROVIDER from .env and returns the matching chat model.

Supported providers:
    - "openai"  -> ChatOpenAI (gpt-4o-mini)
    - "groq"    -> ChatGroq  (llama-3.3-70b-versatile)
"""
import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()

DEFAULT_PROVIDER = "groq"  # change here if .env is missing LLM_PROVIDER


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
        raise RuntimeError(
            "GROQ_API_KEY is missing. Add it to backend/.env "
            "or switch LLM_PROVIDER to 'openai'."
        )

    return ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0.2,
        api_key=api_key,
        max_tokens=600,
    )


def _build_openai():
    from langchain_openai import ChatOpenAI

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is missing. Add it to backend/.env "
            "or switch LLM_PROVIDER to 'groq'."
        )

    return ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.2,
        api_key=api_key,
        max_tokens=600,
    )