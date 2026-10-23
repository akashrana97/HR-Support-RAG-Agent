from pathlib import Path
from app.rag.vectorstore import add_documents
from app.services.ingestion import load_file, chunk_documents

docs = load_file(path=Path(__file__).resolve().parent / "data/sample_kb/company_it_handbook.md")
chunks = chunk_documents(docs=docs)
print(len(docs))

add_documents(chunks)
