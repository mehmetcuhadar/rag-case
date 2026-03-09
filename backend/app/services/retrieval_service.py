from app.services.embedding_service import embedding_service
from app.services.sparse_embedding_service import sparse_embedding_service
from app.repositories.qdrant_repository import qdrant_repository

MAX_DOC_CHARS = 300

class RetrievalService:
    def retrieve(self, query: str, limit: int = 5):
        dense_vector = embedding_service.embed_query(query)
        sparse_vector = sparse_embedding_service.embed_query(query)

        points = qdrant_repository.hybrid_search(dense_vector, sparse_vector, limit=limit)
        points = sorted(points, key=lambda p: p.score, reverse=True)
        sources = []
        docs_for_context = []

        for i, p in enumerate(points, start=1):
            payload = p.payload or {}
            title = payload.get("title") or ""
            url = payload.get("url") or ""
            arxiv_id = payload.get("arxiv_id")
            text = (payload.get("text") or "")[:MAX_DOC_CHARS]

            sources.append({
                "id": i,
                "title": title,
                "url": url,
                "arxiv_id": arxiv_id,
                "score": getattr(p, "score", None),
            })

            # Lightweight context for the LLM (optional, but useful)
            docs_for_context.append(
                f"[{i}] {title}\nURL: {url}\n{text}"
            )

        context = "\n\n---\n\n".join(docs_for_context)

        return context, sources

retrieval_service = RetrievalService()