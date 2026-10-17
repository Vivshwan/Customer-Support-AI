"""
RAG Ingestion Script (Gemini API Mode)
--------------------------------------
Reads all PDFs from backend/knowledge_base/, cleans text, 
generates embeddings via Google Gemini API, and saves a FAISS index.

Run from the backend/ folder:
    python -m rag.ingest
"""
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

# ---------- Paths ----------
BACKEND_DIR = Path(__file__).resolve().parent.parent
KB_PATH = BACKEND_DIR / "knowledge_base"
VECTOR_PATH = BACKEND_DIR / "rag" / "vectorstore" / "faiss_index"

# ---------- Config ----------
# Gemini's recommended model for text embeddings
EMBEDDING_MODEL = "gemini-embedding-001"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 80


# ---------- Text cleaning ----------
def clean_text(text: str) -> str:
    """Fix PyPDF extraction artifacts where every word ends up on its own line."""
    if not text:
        return ""
    text = text.replace("\xa0", " ")
    text = re.sub(r"\n\s*\n+", "\n\n", text)   
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)  
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    return text.strip()


# ---------- Loading ----------
def load_documents():
    if not KB_PATH.exists():
        raise FileNotFoundError(f"Knowledge base folder not found: {KB_PATH}")

    pdf_files = sorted(KB_PATH.glob("*.pdf"))
    if not pdf_files:
        raise FileNotFoundError(f"No PDFs found in {KB_PATH}")

    print(f"Found {len(pdf_files)} PDF(s):")
    for f in pdf_files:
        print(f"  - {f.name}")

    all_docs = []
    for pdf in pdf_files:
        loader = PyPDFLoader(str(pdf))
        docs = loader.load()

        for d in docs:
            d.page_content = clean_text(d.page_content)
            d.metadata["source_file"] = pdf.name

        docs = [d for d in docs if d.page_content]
        all_docs.extend(docs)
        print(f"  Loaded {len(docs)} page(s) from {pdf.name}")

    print(f"\nTotal pages loaded: {len(all_docs)}")
    return all_docs


# ---------- Splitting ----------
def split_documents(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", "? ", "! ", " ", ""],
        length_function=len,
    )
    chunks = splitter.split_documents(docs)
    print(f"Split into {len(chunks)} chunks (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")
    return chunks


# ---------- Embedding + Vector store ----------
def build_vectorstore(chunks):
    print(f"\nLoading API embedding model: {EMBEDDING_MODEL}")
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY is missing in backend/.env")

    # Initialize Gemini Embeddings
    embeddings = GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL,
        google_api_key=api_key
    )

    print("Generating embeddings via Gemini API and building FAISS index...")
    db = FAISS.from_documents(chunks, embeddings)

    VECTOR_PATH.parent.mkdir(parents=True, exist_ok=True)
    db.save_local(str(VECTOR_PATH))
    print(f"\n[OK] Saved vectorstore to: {VECTOR_PATH}")
    return db


# ---------- Main ----------
def main():
    print("=" * 60)
    print(" TechMart RAG Ingestion (Gemini Mode)")
    print("=" * 60)

    docs = load_documents()
    chunks = split_documents(docs)
    build_vectorstore(chunks)

    print("\n" + "=" * 60)
    print(" Ingestion complete.")
    print(f"   Pages:  {len(docs)}")
    print(f"   Chunks: {len(chunks)}")
    print("=" * 60)


if __name__ == "__main__":
    main()