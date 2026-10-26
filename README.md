# HR Support RAG Copilot

A FastAPI and LangGraph assistant for HR policies, leave, benefits, payroll processes, onboarding, offboarding, and employee relations. Answers are grounded in a private Pinecone knowledge base and include document sources and an agent trace.

## Run locally

Requires Python 3.11 or later, a Groq API key, and a Pinecone API key.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set `GROQ_API_KEY`, `PINECONE_API_KEY`, and a strong `ADMIN_API_KEY` in `.env`. Embeddings use the local Hugging Face model configured by `EMBEDDING_MODEL`; its first use downloads model weights.

```bash
python ingest_sample_kb.py
python run.py
```

Open http://localhost:8080. Use **Add HR Document** to upload approved PDF, TXT, Markdown, or DOCX policy documents using the admin key. The `/api/chat`, `/api/ingest`, and `/api/health` endpoints retain their existing contracts.

## Knowledge and migration

The bundled handbook and runbook contain **fictional demo policies**. The assistant must label answers from them as examples. Replace them with approved HR material before using this for actual employee questions, and ingest the approved documents into a clean namespace.

The HR defaults are `PINECONE_INDEX_NAME=hr-support-rag` and `PINECONE_NAMESPACE=company-hr-kb`. Existing IT vectors are not migrated or deleted. Restart the application after changing configuration, then ingest HR documents into the HR namespace. Old IT uploads and audit history remain on disk and are not automatically indexed into the new namespace.

Every substantive question, including the onboarding best-practices example, first retrieves private HR knowledge and grades its relevance. Sufficient evidence produces a private-KB answer. Weak evidence falls back to Tavily, grades the web results, and returns a sourced external answer. Weak web results trigger a query rewrite and another KB-first attempt, up to `MAX_RETRIES`; unresolved questions refer to HR. Greetings and thanks can receive a direct response.

Web fallback is enabled by default and requires `TAVILY_API_KEY`. Set `ENABLE_WEB_FALLBACK=false` to escalate weak private evidence without external search. Fallback queries are sent to an external search provider; avoid sensitive employee information. External guidance cannot establish company policy or individual entitlements.

## Scope and data handling

The copilot explains documented processes. It cannot approve leave, view balances, change employee records, determine eligibility, or resolve employment disputes. Individual and sensitive cases should use approved HR channels. Do not upload employee records, bank details, medical information, or confidential case files. This application has an admin key for ingestion, but does not implement employee authentication or document-level authorization. Chat questions and traces are stored in the local SQLite audit database. Groq receives questions and retrieved context; Pinecone stores embedded document content.

The `demo/Agentic_RAG.ipynb` notebook is an archived generic RAG experiment, not the application entry point or HR knowledge source.

## Checks

```bash
python -m unittest discover -s tests
```
