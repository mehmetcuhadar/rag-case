from sentence_transformers import SentenceTransformer
from app.core.config import settings


class EmbeddingService:
    def __init__(self):
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=True
        )
        return embeddings.tolist()

    def embed_query(self, text: str) -> list[float]:
        emb = self.model.encode(
            [text],
            normalize_embeddings=True
        )
        return emb[0].tolist()


embedding_service = EmbeddingService()