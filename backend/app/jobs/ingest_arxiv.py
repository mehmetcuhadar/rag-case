from datasets import load_dataset
from app.core.config import settings
from app.repositories.qdrant_repository import qdrant_repository
from app.services.embedding_service import embedding_service
from app.services.sparse_embedding_service import sparse_embedding_service
import re

ARXIV_CODE_RE = re.compile(r"\(([^)]+)\)\s*$")

def build_text(title, abstract):
    title = (title or "").strip()
    abstract = (abstract or "").strip()

    return f"Title: {title}\n\nAbstract:\n{abstract}".strip()

def subject_code(ps: str | None) -> str | None:
    if not ps:
        return None
    m = ARXIV_CODE_RE.search(ps.strip())
    return m.group(1) if m else None

def run(batch_size: int = 128):
    print("MODEL_NAME =", settings.MODEL_NAME)
    print("EMBEDDING MODEL  =", settings.EMBEDDING_MODEL)
    print("EMBEDDING DIM  =", settings.EMBEDDING_DIM)
    print("QDRANT_COLLECTION =", settings.QDRANT_COLLECTION)

    dataset = load_dataset(settings.ARXIV_DATASET, split="train")

    dataset = dataset.filter(lambda x: subject_code(x.get("primary_subject")) == settings.ARXIV_SUBJECT)

    dataset = dataset.select(range(min(settings.ARXIV_LIMIT, len(dataset))))

    qdrant_repository.ensure_collection()

    texts, payloads = [], []
    total = 0

    for row in dataset:
        arxiv_id = row.get("arxiv_id")
        text = build_text(row.get("title"), row.get("abstract"))

        texts.append(text)
        payloads.append({
            "arxiv_id": arxiv_id,
            "title": row.get("title"),
            "url": f"https://arxiv.org/abs/{arxiv_id}",
            "primary_subject": row.get("primary_subject"),
            "submission_date": row.get("submission_date"),
            "text": text,
        })

        if len(texts) >= batch_size:
            dense_vectors = embedding_service.embed_documents(texts)
            sparse_vectors = sparse_embedding_service.embed_documents(texts)
            qdrant_repository.upsert(dense_vectors, sparse_vectors, payloads)
            total += len(texts)
            print(f"Upserted: {total}")
            texts, payloads = [], []

    if texts:
        dense_vectors = embedding_service.embed_documents(texts)
        sparse_vectors = sparse_embedding_service.embed_documents(texts)
        qdrant_repository.upsert(dense_vectors, sparse_vectors, payloads)
        total += len(texts)

    print("Ingest completed. Total:", total)

if __name__ == "__main__":
    run()