from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from app.core.config import (QDRANT_API_KEY, QDRANT_URL, PINECONE_API_KEY, VECTOR_PROVIDER, EMBEDDING_DIMENSION)
from app.core.loger import setup_logging
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from pinecone import Pinecone, ServerlessSpec

logger = setup_logging(__name__)


class VectorStoreClient(ABC):
    """
    Interface commune pour un backend vectoriel. Le reste du pipeline
    (indexation, retrieval) ne doit dependre que de cette interface, jamais
    directement de Qdrant ou Pinecone -> permet de switcher de backend en
    changeant uniquement VECTOR_PROVIDER dans la config.
    """

    @abstractmethod
    def create_or_get_index(self) -> None:
        """Cree la collection/l'index si elle n'existe pas deja."""

    @abstractmethod
    def upsert(
        self,
        ids: List[str],
        vectors: List[List[float]],
        metadatas: List[Dict[str, Any]],
    ) -> None:

        """Insere ou met a jour des vecteurs avec leurs metadata."""

    @abstractmethod
    def query(
        self,
        vector: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Recherche les top_k vecteurs les plus proches, avec filtres optionnels sur metadata."""


class QdrantVectorStore(VectorStoreClient):
    """
    Implementation Qdrant. La connexion et la creation de la collection
    sont faites des l'instanciation 
    """

    def __init__(self, collection_name: str = "douane", vector_size: int = EMBEDDING_DIMENSION):
        self.collection_name = collection_name
        self.vector_size = vector_size
        self.client: Optional[QdrantClient] = None
        self._connect()
        self.create_or_get_index()

    def _connect(self) -> None:
        try:
            self.client = QdrantClient(api_key=QDRANT_API_KEY, url=QDRANT_URL)
            logger.info("Client Qdrant connecte avec succes")
        except Exception as e:
            raise RuntimeError(f"Erreur lors de la connexion au client Qdrant: {e}") from e

    def create_or_get_index(self) -> None:
        try:
            if not self.client.collection_exists(self.collection_name):
                logger.info(f"Creation de la collection Qdrant '{self.collection_name}'")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                        ),
                )
                logger.info(f"Collection '{self.collection_name}' creee avec succes")
            else:
                logger.info(f"Collection '{self.collection_name}' deja existante")
        except Exception as e:
            raise RuntimeError(f"Erreur lors de la creation de la collection Qdrant: {e}") from e

    def upsert(self, ids: List[str], 
    vectors: List[List[float]], 
    metadatas: List[Dict[str, Any]]
    ) -> None:
        points = [
            PointStruct(id=point_id, vector=vector, payload=metadata)
            for point_id, vector, metadata in zip(ids, vectors, metadatas)
        ]
        self.client.upsert(collection_name=self.collection_name, points=points)
        logger.info(f"{len(points)} point(s) upsert dans '{self.collection_name}'")

    def query(self, vector: List[float], 
    top_k: int = 5, 
    filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=vector,
            limit=top_k,
            query_filter=filters,
        )
        return [{"id": p.id, "score": p.score, "payload": p.payload} for p in results.points]


class PineconeVectorStore(VectorStoreClient):
    def __init__(self, index_name: str = "docmind", dimension: int = EMBEDDING_DIMENSION):
        self.index_name = index_name
        self.dimension = dimension
        self.client = Pinecone(api_key=PINECONE_API_KEY)
        self.create_or_get_index()
        self.index = self.client.Index(self.index_name)

    def create_or_get_index(self) -> None:
        try:
            if not self.client.has_index(self.index_name):
                logger.info(f"Creation de l'index Pinecone '{self.index_name}'")
                self.client.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region="us-west-1"),
                )
                logger.info(f"Index '{self.index_name}' cree avec succes")
            else:
                logger.info(f"Index '{self.index_name}' deja existant")
        except Exception as e:
            raise RuntimeError(f"Erreur lors de la creation de l'index Pinecone: {e}") from e

    def upsert(self, ids: List[str], vectors: List[List[float]], metadatas: List[Dict[str, Any]]) -> None:
        self.index.upsert(vectors=list(zip(ids, vectors, metadatas)))
        logger.info(f"{len(ids)} vecteur(s) upsert dans l'index '{self.index_name}'")

    def query(self, vector: List[float], top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        results = self.index.query(vector=vector, top_k=top_k, filter=filters, include_metadata=True)
        return [
            {"id": match["id"], "score": match["score"], "payload": match.get("metadata", {})}
            for match in results["matches"]
        ]


def get_vector_store_client(**kwargs) -> VectorStoreClient:
    """
    Factory : instancie le backend vectoriel actif selon VECTOR_PROVIDER
    (dans app/core/config.py). C'est le seul endroit du code qui doit
    connaitre l'existence de Qdrant/Pinecone - partout ailleurs, on manipule
    un VectorStoreClient generique.
    """
    provider = (VECTOR_PROVIDER or "qdrant").lower()

    if provider == "qdrant":
        return QdrantVectorStore(**kwargs)
    elif provider == "pinecone":
        return PineconeVectorStore(**kwargs)
    else:
        raise ValueError(f"VECTOR_DB_PROVIDER inconnu: '{provider}' (attendu: 'qdrant' ou 'pinecone')")