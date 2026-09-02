from typing import Any, Dict, List, Optional
from pathlib import Path

from llama_index.core.storage.docstore import SimpleDocumentStore

from app.core.config import EMBEDDING_MODEL_NAME
from app.core.loger import setup_logging
from app.services.embeddings.embedding_huggingface import EmbeddingModels
from app.services.vectorstores._vector_store_client import get_vector_store_client

logger = setup_logging(__name__)

DOCSTORE_FILE = Path("data/docstore.json")


class Retriever:
    """
    Récupère les Leaf Nodes les plus pertinents par similarité vectorielle
    et résout optionnellement leurs nœuds parents (Articles complets)
    depuis le DocStore.
    """

    def __init__(
        self,
        embedding_model_name: str = EMBEDDING_MODEL_NAME,
        docstore_path: Path = DOCSTORE_FILE
    ):
        self.embedder = EmbeddingModels(model_name=embedding_model_name).get_embeddings()
        if self.embedder is None:
            raise RuntimeError("Impossible de charger le modèle d'embedding pour le retriever.")
        
        self.vector_store = get_vector_store_client()
        self.docstore_path = docstore_path
        self._docstore: Optional[SimpleDocumentStore] = None

    @property
    def docstore(self) -> Optional[SimpleDocumentStore]:
        """Lazy loading du DocStore pour ne le charger en mémoire qu'au besoin."""
        if self._docstore is None and self.docstore_path.exists():
            try:
                self._docstore = SimpleDocumentStore.from_persist_path(str(self.docstore_path))
                logger.info("DocStore chargé avec succès dans le Retriever.")
            except Exception as e:
                logger.error(f"Erreur lors du chargement du DocStore : {e}")
                self._docstore = None
        return self._docstore

    def retrieve(
        self,
        query: str,
        top_k: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        fetch_parent_context: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Effectue une recherche vectorielle dans Qdrant.

        Args:
            query: Requête en langage naturel.
            top_k: Nombre de candidats bruts à récupérer (soumis au Reranker ensuite).
            filters: Filtres sur métadonnées Qdrant (ex: {"domain": "Douanes Benin"}).
            fetch_parent_context: Si True, résout le texte complet de l'article parent
                                  depuis le DocStore.

        Returns:
            Liste de dictionnaires contenant le texte, score, métadonnées et contexte parent.
        """
        if not query or not query.strip():
            logger.warning("Requête vide, aucun retrieval effectué.")
            return []

        # 1. Vectorisation de la requête
        query_vector = self.embedder.embed_query(query)

        # 2. Recherche vectorielle dans Qdrant
        raw_results = self.vector_store.query(
            vector=query_vector,
            top_k=top_k,
            filters=filters
        )

        formatted_candidates: List[Dict[str, Any]] = []

        # 3. Normalisation des résultats et résolution du Parent Node
        for idx, res in enumerate(raw_results, start=1):
            payload = res.get("payload", {})
            leaf_text = payload.get("text", "")
            parent_id = payload.get("parent_id")
            node_id = payload.get("llama_node_id")
            score = res.get("score", 0.0)

            parent_text = None
            if fetch_parent_context and parent_id and self.docstore:
                try:
                    parent_node = self.docstore.get_document(parent_id, raise_error=False)
                    if parent_node:
                        parent_text = parent_node.get_content()
                except Exception as e:
                    logger.debug(f"Impossible de récupérer le nœud parent {parent_id}: {e}")

            candidate = {
                "id": node_id,
                "score": score,
                "text": leaf_text,
                "parent_text": parent_text or leaf_text,  # Fallback sur le texte enfant si le parent manque
                "parent_id": parent_id,
                "metadata": {
                    "domain": payload.get("domain", "Général"),
                    "article_number": payload.get("article_number", "N/A"),
                    "file_name": payload.get("file_name", payload.get("source", "Inconnu")),
                    "source": payload.get("source", "Inconnu"),
                }
            }
            formatted_candidates.append(candidate)

        logger.info(
            f"🔍 Retriever : {len(formatted_candidates)} candidat(s) extrait(s) "
            f"pour la requête '{query[:50]}...'"
        )
        return formatted_candidates