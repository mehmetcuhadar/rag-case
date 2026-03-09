from fastembed import SparseTextEmbedding
from qdrant_client.http.models import SparseVector

class SparseEmbeddingService:
    def __init__(self):
        self.model = SparseTextEmbedding("Qdrant/bm25")

    def embed_documents(self, texts: list[str]) -> list[SparseVector]:
        out = []
        for e in self.model.embed(texts):  # e is fastembed SparseEmbedding
            out.append(
                SparseVector(
                    indices=e.indices.tolist(),
                    values=e.values.tolist(),
                )
            )
        return out

    def embed_query(self, text: str) -> SparseVector:
        e = next(self.model.embed([text]))  # SparseEmbedding
        return SparseVector(
            indices=e.indices.tolist(),
            values=e.values.tolist(),
        )

sparse_embedding_service = SparseEmbeddingService()