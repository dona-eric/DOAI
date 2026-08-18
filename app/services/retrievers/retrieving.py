from typing import Any, Dict, List, Optional
from app.core.config import EMBEDDING_MODEL_NAME
from app.core.loger import setup_logging
from app.services.embeddings.embedding_huggingface import EmbeddingModels
from app.services.vectorstores._vector_store_client import get_vector_store_client

logger = setup_logging(__name__)


class Retriever:
    """
    Récupère les passages les plus proches d'une requête depuis la DB
    vectorielle active. Le top_k ici est volontairement large (candidats
    bruts, par similarité cosinus) : le reranking se charge ensuite de
    ne garder que les meilleurs par pertinence réelle.
    """

    def __init__(self, embedding_model_name: str = EMBEDDING_MODEL_NAME):
        self.embedder = EmbeddingModels(model_name=embedding_model_name).get_embeddings()
        if self.embedder is None:
            raise RuntimeError("Impossible de charger le modèle d'embedding pour le retriever.")
        self.vector_store = get_vector_store_client()

    def retrieve(self, query: str, top_k: int = 20,filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        filters permet de restreindre la recherche via les métadonnées
        déjà présentes sur chaque vecteur (ex: {"domain": "Douanes Benin"}
        ou {"level": "article"}) — utile pour cibler CorridorCheck vs
        DocMind AI si les deux partagent la même collection.
        """
        if not query or not query.strip():
            logger.warning("Requête vide, aucun retrieval effectué.")
            return []

        query_vector = self.embedder.embed_query(query)
        results = self.vector_store.query(vector=query_vector, top_k=top_k, filters=filters)

        logger.info(f"{len(results)} candidat(s) récupéré(s) pour la requête : '{query[:60]}'")
        return results