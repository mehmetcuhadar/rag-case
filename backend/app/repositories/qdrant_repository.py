from qdrant_client import QdrantClient, models
from qdrant_client.http.models import (
    Distance, VectorParams, PointStruct, SparseVectorParams, SparseVector
)
import uuid

from app.core.config import settings


class QdrantRepository:

    def __init__(self):
        self.client = QdrantClient(url=settings.QDRANT_URL)
        self.collection = settings.QDRANT_COLLECTION

    def ensure_collection(self):

        collections = self.client.get_collections().collections
        names = [c.name for c in collections]

        if self.collection in names:
            return

        self.client.create_collection(
            collection_name=self.collection,
            vectors_config={
                "dense": VectorParams(
                    size=settings.EMBEDDING_DIM,
                    distance=Distance.COSINE
                )
            },
            sparse_vectors_config={
                "sparse": SparseVectorParams()
            }
        )

    def upsert(self, dense_vectors, sparse_vectors, payloads):

        points = []

        for dense_vec, sparse_vec, payload in zip(dense_vectors, sparse_vectors, payloads):

            points.append(
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector={
                        "dense": dense_vec,
                        "sparse": sparse_vec
                    },
                    payload=payload
                )
            )

        self.client.upsert(
            collection_name=self.collection,
            points=points
        )

    def search(self, vector, sparse_vector, limit=5):

        result = self.client.search(
            collection_name=self.collection,
            query_vector=vector,
            query_sparse_vector=sparse_vector,
            limit=limit,
            with_payload=True
        )

        return result

    def hybrid_search(self, dense_vector, sparse_vector: SparseVector, limit=5):
        # IMPORTANT: prefetch limit should be >= final limit (often higher for better fusion)
        prefetch_limit = max(20, limit)

        res = self.client.query_points(
            collection_name=self.collection,
            prefetch=[
                models.Prefetch(
                    query=sparse_vector,   # SparseVector(indices=[...], values=[...])
                    using="sparse",
                    limit=prefetch_limit,
                ),
                models.Prefetch(
                    query=dense_vector,    # list[float]
                    using="dense",
                    limit=prefetch_limit,
                ),
            ],
            query=models.FusionQuery(fusion=models.Fusion.DBSF),
            limit=limit,
            with_payload=True,
        )

        # Depending on client version, results may be in res.points
        return getattr(res, "points", res)

qdrant_repository = QdrantRepository()