"""Index fictional HR demo policies into the configured knowledge namespace."""
from pathlib import Path
from app.core.config import get_settings
from app.services.ingestion import load_file, chunk_documents, SUPPORTED
from app.rag.vectorstore import add_documents


def main():
    settings = get_settings()
    folder = Path(settings.sample_kb_dir)
    files = sorted(p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in SUPPORTED)
    if not files:
        raise RuntimeError(f"No supported HR knowledge documents found in {folder}")
    all_docs = []
    for path in files:
        all_docs.extend(load_file(path))
    chunks = chunk_documents(all_docs)
    # Preserve demo provenance even when splitting removes the document heading.
    for chunk in chunks:
        chunk.page_content = "[Fictional HR demo policy — not approved company policy.]\n" + chunk.page_content
        chunk.metadata['demo'] = True
    ids = add_documents(chunks)
    print(f"Indexed {len(files)} HR demo files -> {len(chunks)} chunks -> {len(ids)} Pinecone vectors")


if __name__ == '__main__':
    main()
