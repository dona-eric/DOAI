from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from app.core.config import (EMBEDDING_DIMENSION,PINECONE_API_KEY,QDRANT_API_KEY,QDRANT_URL,VECTOR_PROVIDER,timer)
from app.core.loger import setup_logging
from pinecone import Pinecone, ServerlessSpec
from qdrant_client import QdrantClient
from qdrant_client.models import (Distance, FieldCondition, Filter,MatchValue,PointStruct, VectorParams,)

logger = setup_logging(__name__)


class VectorStoreClient(ABC):
    """Interface abstraite unifiée pour les backends vectoriels."""

    @abstractmethod
    def create_or_get_index(self) -> None:
        """Crée la collection/l'index si elle n'existe pas déjà."""

    @abstractmethod
    def upsert(self,ids: List[str],vectors: List[List[float]],metadatas: List[Dict[str, Any]],) -> None:
        """Insère ou met à jour des vecteurs avec leurs métadonnées."""

    @abstractmethod
    def query(self, vector: List[float],top_k: int = 5,filters: Optional[Dict[str, Any]] = None,) -> List[Dict[str, Any]]:
        """Recherche les top_k vecteurs les plus proches avec filtres optionnels."""


class QdrantVectorStore(VectorStoreClient):
    """Implémentation robuste du client Qdrant."""

    def __init__(self,collection_name: str = "douane",vector_size: int = EMBEDDING_DIMENSION):
        self.collection_name = collection_name
        self.vector_size = vector_size
        self.client: Optional[QdrantClient] = None
        self._connect()
        self.create_or_get_index()

    def _connect(self) -> None:
        try:
            self.client = QdrantClient(
                api_key=QDRANT_API_KEY, url=QDRANT_URL, timeout=120
            )
            logger.info("Client Qdrant connecté avec succès.")
        except Exception as e:
            raise RuntimeError(
                f"Erreur de connexion au cluster Qdrant : {e}"
            ) from e

    @timer
    def create_or_get_index(self) -> None:
        try:
            if not self.client.collection_exists(self.collection_name):
                logger.info(
                    f"Création de la collection Qdrant '{self.collection_name}'"
                )
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size, distance=Distance.COSINE
                    ),
                )
                logger.info(
                    f"Collection '{self.collection_name}' créée avec succès."
                )
            else:
                logger.info(
                    f"Collection Qdrant '{self.collection_name}' existante."
                )
        except Exception as e:
            raise RuntimeError(
                f"Erreur lors de la création de la collection Qdrant : {e}"
            ) from e

    def _build_qdrant_filter(
        self, filters: Optional[Dict[str, Any]]
    ) -> Optional[Filter]:
        """Convertit un dictionnaire Python standard en objet Filter natif Qdrant."""
        if not filters:
            return None

        conditions = []
        for key, value in filters.items():
            if value is not None:
                conditions.append(
                    FieldCondition(key=key, match=MatchValue(value=value))
                )

        return Filter(must=conditions) if conditions else None

    @timer
    def upsert(self, ids: List[str],vectors: List[List[float]],metadatas: List[Dict[str, Any]],) -> None:
        points = [
            PointStruct(id=point_id, vector=vector, payload=metadata)
            for point_id, vector, metadata in zip(ids, vectors, metadatas)
        ]
        self.client.upsert(collection_name=self.collection_name, points=points)
        logger.info(
            f"{len(points)} points enregistrés dans Qdrant ('{self.collection_name}')."
        )

    def query(self,vector: List[float],top_k: int = 5,filters: Optional[Dict[str, Any]] = None,) -> List[Dict[str, Any]]:
        qdrant_filter = self._build_qdrant_filter(filters)

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=vector,
            limit=top_k,
            query_filter=qdrant_filter,
        )
        return [
            {"id": p.id, "score": p.score, "payload": p.payload}
            for p in results.points
        ]


class PineconeVectorStore(VectorStoreClient):
    """Implémentation du client Pinecone."""

    def __init__(
        self,
        index_name: str = "docmind",
        dimension: int = EMBEDDING_DIMENSION,
    ):
        self.index_name = index_name
        self.dimension = dimension
        self.client = Pinecone(api_key=PINECONE_API_KEY)
        self.create_or_get_index()
        self.index = self.client.Index(self.index_name)

    def create_or_get_index(self) -> None:
        try:
            if not self.client.has_index(self.index_name):
                logger.info(
                    f"Création de l'index Pinecone '{self.index_name}'"
                )
                self.client.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region="us-west-1"),
                )
                logger.info(f"Index Pinecone '{self.index_name}' créé.")
            else:
                logger.info(f"Index Pinecone '{self.index_name}' existant.")
        except Exception as e:
            raise RuntimeError(
                f"Erreur de création de l'index Pinecone : {e}"
            ) from e

    def upsert(
        self,
        ids: List[str],
        vectors: List[List[float]],
        metadatas: List[Dict[str, Any]],
    ) -> None:
        # Structure conforme aux attentes de l'API Pinecone v3+
        vectors_payload = [
            {"id": vec_id, "values": vec, "metadata": meta}
            for vec_id, vec, meta in zip(ids, vectors, metadatas)
        ]
        self.index.upsert(vectors=vectors_payload)
        logger.info(
            f"{len(ids)} vecteurs insérés dans Pinecone ('{self.index_name}')."
        )

    def query(
        self,
        vector: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        results = self.index.query(
            vector=vector, top_k=top_k, filter=filters, include_metadata=True
        )
        return [
            {
                "id": match["id"],
                "score": match["score"],
                "payload": match.get("metadata", {}),
            }
            for match in results["matches"]
        ]


def get_vector_store_client(**kwargs) -> VectorStoreClient:
    """Factory d'instanciation selon le VECTOR_PROVIDER actif."""
    provider = (VECTOR_PROVIDER or "qdrant").lower()

    if provider == "qdrant":
        return QdrantVectorStore(**kwargs)
    elif provider == "pinecone":
        return PineconeVectorStore(**kwargs)
    else:
        raise ValueError(
            f"VECTOR_PROVIDER non géré : '{provider}'. Attendu : 'qdrant' ou 'pinecone'."
        )