# 🤖 TechMart Multi-Agent AI Customer Support Assistant

> **Industry-level capstone project** demonstrating Multi-Agent Systems, Retrieval-Augmented Generation (RAG), vector databases, LLM integration, and full-stack cloud development.

A production-style AI customer support system where **five specialized AI agents** handle different customer query domains, routed by an intelligent intent-detection layer and grounded in a company knowledge base via RAG.

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Setup & Installation](#-setup--installation)
- [Usage](#-usage)
- [API Endpoints](#-api-endpoints)
- [Testing & Results](#-testing--results)
- [Learning Outcomes](#-learning-outcomes)
- [Roadmap](#-roadmap)
- [License](#-license)

---

## 🎯 Overview

Traditional chatbots use a single generic model that struggles with domain-specific questions. This project solves that with a **multi-agent architecture**:

- A **central orchestrator** detects intent and routes queries
- **Five specialized agents** — Billing, Technical, Product, Complaint, FAQ
- **RAG pipeline** grounds every answer in real company documents
- **Multi-intent support** — one question can engage multiple agents
- **Full authentication** with JWT and per-user conversation history
- **Analytics dashboard** for usage insights

Built as a capstone project to demonstrate modern AI engineering practices.

---

## ✨ Key Features

### 🧠 Multi-Agent System
- 5 domain-specialized agents with unique prompts and personas
- Central router dispatches to one or more agents per query
- Parallel execution for multi-intent queries (~2x faster)

### 📚 Retrieval-Augmented Generation (RAG)
- 6 knowledge base PDFs (FAQ, Refund, Shipping, Warranty, Pricing, User Manual)
- ~500-char chunking with overlap
- `sentence-transformers/all-MiniLM-L6-v2` embeddings
- FAISS vector store — 95 chunks indexed
- Top-4 semantic retrieval per query

### 🤖 LLM Integration
- Groq (Llama 3.3 70B) or OpenAI GPT-4o-mini (switchable via env var)
- Strict grounding prompts to prevent hallucination
- Explicit refusal when context is missing

### 👤 Authentication & Multi-User
- JWT-based registration/login
- bcrypt password hashing
- Protected routes — users only see their own data
- Persistent conversations across sessions

### 💬 Chat Interface
- Real-time typing indicators
- Multi-agent response cards with color-coded badges
- Source citations displayed per answer
- Conversation sidebar with auto-generated titles

### 📊 Analytics Dashboard
- Conversation and message totals
- Agent usage bar chart
- 7-day activity line chart
- Recent conversations table

---

## 🏛️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                    FRONTEND (React)                  │
│  Login/Register  │  Chat UI + Sidebar  │  Dashboard │
└─────────────┬───────────────┬───────────────┬───────┘
              │               │               │
              │  HTTPS + JWT  │               │
              ▼               ▼               ▼
┌─────────────────────────────────────────────────────┐
│                  FASTAPI BACKEND                     │
│  /auth  │  /chat  │  /conversations  │  /analytics  │
└─────────┬───────────────────┬───────────────────────┘
          │                   │
          ▼                   ▼
┌──────────────────┐  ┌───────────────────────┐
│  INTENT DETECTOR │  │   MongoDB (Motor)     │
│  (LLM-based)     │  │  users, conversations │
└────────┬─────────┘  │  messages             │
         │            └───────────────────────┘
         ▼
┌──────────────────────────────────────┐
│         AGENT ROUTER                 │
├──────────┬──────────┬────────────────┤
│ Billing  │Technical │ Product  ...   │
└────┬─────┴────┬─────┴────────┬───────┘
     │          │              │
     └──────────┴──────────────┘
                │
                ▼
     ┌─────────────────────┐
     │   RAG PIPELINE      │
     │ FAISS → Top-4 chunks│
     └──────────┬──────────┘
                │
                ▼
     ┌─────────────────────┐
     │   LLM (Groq/OpenAI) │
     │  Grounded response  │
     └─────────────────────┘
```

---

## 🛠️ Tech Stack

| Category | Technology |
|---|---|
| Backend | Python 3.11, FastAPI, Uvicorn |
| AI/LLM | LangChain, LangGraph, Groq, OpenAI |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Vector DB | FAISS |
| Database | MongoDB (Motor async driver) |
| Auth | python-jose (JWT), passlib (bcrypt) |
| Frontend | React 18, TypeScript, Vite |
| Styling | Tailwind CSS v4 |
| Charts | Recharts |
| Routing | React Router v6 |
| HTTP Client | Axios |

---

## 📁 Project Structure

```
customer-support-ai/
├── backend/
│   ├── main.py                    # FastAPI app + routes
│   ├── requirements.txt
│   ├── Procfile                   # Railway deployment
│   ├── runtime.txt                # Python version
│   ├── .env                       # (gitignored) secrets
│   │
│   ├── agents/                    # AI agents
│   │   ├── llm.py                 # LLM factory (Groq/OpenAI)
│   │   ├── intent.py              # Intent classifier
│   │   ├── router.py              # Agent dispatcher
│   │   ├── billing.py
│   │   ├── technical.py
│   │   ├── product.py
│   │   ├── complaint.py
│   │   └── faq.py
│   │
│   ├── rag/                       # Retrieval-Augmented Generation
│   │   ├── ingest.py              # PDF ingestion script
│   │   ├── retriever.py           # Query-time retrieval
│   │   └── vectorstore/           # (gitignored) FAISS index
│   │
│   ├── auth/                      # Authentication
│   │   ├── security.py            # JWT + bcrypt utilities
│   │   ├── dependencies.py        # get_current_user
│   │   └── routes.py              # /register, /login, /me
│   │
│   ├── database/                  # MongoDB layer
│   │   ├── users.py
│   │   └── memory.py              # Conversations + messages
│   │
│   ├── routes/                    # Additional routers
│   │   └── analytics.py
│   │
│   └── knowledge_base/            # Company PDF documents
│       ├── FAQ.pdf
│       ├── RefundPolicy.pdf
│       ├── ShippingPolicy.pdf
│       ├── Warranty.pdf
│       ├── Pricing.pdf
│       └── UserManual.pdf
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── types.ts
│   │   ├── api/client.ts
│   │   ├── auth/
│   │   │   ├── AuthContext.tsx
│   │   │   └── ProtectedRoute.tsx
│   │   ├── pages/
│   │   │   ├── LoginPage.tsx
│   │   │   ├── RegisterPage.tsx
│   │   │   └── AnalyticsPage.tsx
│   │   ├── components/
│   │   │   ├── ChatWindow.tsx
│   │   │   ├── ChatInput.tsx
│   │   │   ├── MessageBubble.tsx
│   │   │   ├── AgentResponseCard.tsx
│   │   │   ├── TypingIndicator.tsx
│   │   │   └── Sidebar.tsx
│   │   └── hooks/
│   │       └── useChat.ts
│   ├── package.json
│   └── vite.config.ts
│
└── README.md
```

---

## 🚀 Setup & Installation

### Prerequisites

- Python 3.11+
- Node.js 20+
- MongoDB (local or Atlas)
- Groq API key (free: https://console.groq.com/keys) **OR** OpenAI API key

### 1. Clone the Repository

```bash
git clone https://github.com/Vivshwan/Customer-Support-AI.git
cd Customer-Support-AI
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create `backend/.env`:

```env
# LLM Provider (choose "groq" or "openai")
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_your_groq_key_here
OPENAI_API_KEY=sk-your-openai-key-here   # optional

# MongoDB
MONGODB_URI=mongodb://127.0.0.1:27017

# JWT
JWT_SECRET=replace_with_a_long_random_string
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60

# App
APP_ENV=development
```

### 4. Ingest Knowledge Base (one-time)

```bash
python -m rag.ingest
```

Expected output: `Ingestion complete. Pages: 22, Chunks: 95`

### 5. Start the Backend

```bash
uvicorn main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

### 6. Frontend Setup

```bash
cd ../frontend
npm install
npm run dev
```

Frontend: http://localhost:5173

---

## 💡 Usage

1. **Register** a new account at http://localhost:5173/register
2. **Start a chat** by clicking "+ New chat"
3. **Ask a question** — try these examples:

| Query | What to expect |
|---|---|
| `What is your refund policy?` | Billing agent card |
| `How do I reset my password?` | Technical agent card |
| `I paid yesterday but Premium is still locked.` | **Two agent cards** (Billing + Technical) |
| `My laptop won't turn on and I want a refund.` | **Two agent cards** (Technical + Billing) |
| `How much does the Pro 14 cost?` | Product agent card |
| `What's the capital of France?` | Refusal (out of scope) |

4. **View analytics** by clicking "📊 View analytics" in the sidebar
5. **Browse history** by clicking any past conversation in the sidebar

---

## 🔌 API Endpoints

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Create new user |
| POST | `/auth/login` | Get JWT token |
| GET | `/auth/me` | Get current user |

### Conversations

| Method | Endpoint | Description |
|---|---|---|
| POST | `/conversations` | Create new conversation |
| GET | `/conversations` | List user's conversations |
| GET | `/conversations/{id}` | Get conversation + messages |
| DELETE | `/conversations/{id}` | Delete conversation |

### Chat

| Method | Endpoint | Description |
|---|---|---|
| POST | `/chat` | Send message → agent response |

### Analytics

| Method | Endpoint | Description |
|---|---|---|
| GET | `/analytics/summary` | Usage stats for user |

### Health

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Service info |
| GET | `/health` | Deep health check |

**All endpoints except `/auth/*` and `/health` require JWT in `Authorization: Bearer <token>` header.**

---

## 🧪 Testing & Results

### Retrieval Accuracy

| Query | Top-1 Source | Score | Correct? |
|---|---|---|---|
| "What is the refund policy?" | RefundPolicy.pdf | 0.766 | ✅ |
| "How long does shipping take?" | FAQ.pdf | 0.650 | ✅ |
| "I paid for Premium but it's locked" | UserManual.pdf | 0.489 | ✅ |

### Intent Classification

| Query | Detected Intents |
|---|---|
| "How do I reset my password?" | `['technical']` |
| "What is your refund policy?" | `['billing']` |
| **"I paid yesterday but Premium is locked"** | `['billing', 'technical']` ⭐ |
| **"My laptop won't turn on and I want a refund"** | `['technical', 'billing']` ⭐ |
| "What's the capital of France?" | `['faq']` → refusal |

### Anti-Hallucination Test

Query: `What's the capital of France?`
Response: `"I don't have that information in my knowledge base. Let me connect you with a human agent."` ✅

---

## 🎓 Learning Outcomes

This project demonstrates proficiency in:

- **Multi-Agent Systems** — orchestration, routing, specialized prompts
- **Retrieval-Augmented Generation** — chunking, embeddings, semantic search
- **Vector Databases** — FAISS indexing and querying
- **Large Language Models** — prompt engineering, grounding, temperature control
- **REST API Design** — FastAPI, Pydantic, async I/O
- **Authentication** — JWT, bcrypt, protected routes
- **Database Design** — MongoDB collections, indexes, async queries
- **Full-Stack Development** — React, TypeScript, Tailwind
- **Cloud Deployment** — Railway, Vercel, MongoDB Atlas

---

## 🗺️ Roadmap

- [x] Phase 1 — Project skeleton
- [x] Phase 2 — RAG pipeline
- [x] Phase 3 — LLM integration + FAQ agent
- [x] Phase 4 — Intent detection + router
- [x] Phase 5 — Full 5-agent suite
- [x] Phase 6 — FastAPI + MongoDB
- [x] Phase 7 — React chat UI
- [x] Phase 8 — JWT auth + conversations
- [ ] Phase 9 — Analytics dashboard
- [ ] Phase 10 — Cloud deployment

### Future Enhancements
- 🎙️ Voice-enabled support
- 🌍 Multilingual conversations
- 😊 Sentiment analysis for routing
- 🎫 Automatic ticket creation
- 👤 Human-agent handoff
- 📧 Email / WhatsApp integration
- 🤖 AI-generated conversation summaries

---

## 📝 License

This project is developed as an educational capstone. Free to use, modify, and learn from.

---

## 🙏 Acknowledgments

- LangChain documentation and community
- Groq for generous free-tier LLM inference
- MongoDB Atlas for free-tier database hosting
- Hugging Face for open embedding models

---

**Built with ❤️ as a demonstration of modern AI engineering practices.**