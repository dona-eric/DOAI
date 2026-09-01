import json
from pathlib import Path
from typing import Any, Dict, List
import uuid

from llama_index.core.schema import BaseNode

from app.core.config import EMBEDDING_MODEL_NAME, timer
from app.core.loger import setup_logging
from app.services.embeddings.embedding_huggingface import EmbeddingModels
from app.services.processing.chuncker import chuncking_hierachical
from app.services.processing.parser import ParserDocuments
from app.services.vectorstores._vector_store_client import get_vector_store_client
from app.services.processing.loader import get_files

logger = setup_logging(__name__)

BATCH_SIZE_NODES = 128
BATCH_SIZE_DOCS = 3
STATE_FILE = Path("data/ingestion_state.json")
DOCSTORE_FILE = Path("data/docstore.json")

# INGESTION STATE
# ============================================================


def load_ingestion_state() -> Dict[str, Any]:
    if not STATE_FILE.exists():
        return {"processed_documents": []}

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Impossible de lire le fichier d'état : {e}")
        return {"processed_documents": []}


def save_ingestion_state(state: Dict[str, Any]) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4, ensure_ascii=False)


def _clean_metadata(node: BaseNode, domain: str, text: str) -> Dict[str, Any]:
    """Nettoie et prépare les métadonnées pour Qdrant."""
    metadata = dict(node.metadata) if node.metadata else {}

    metadata["domain"] = domain
    metadata["llama_node_id"] = node.node_id
    metadata["parent_id"] = (
        node.parent_node.node_id if node.parent_node else None
    )
    metadata["text"] = text

    cleaned_metadata = {}
    for key, value in metadata.items():
        if value is not None:
            if isinstance(value, (str, int, float, bool, list)):
                cleaned_metadata[key] = value
            else:
                cleaned_metadata[key] = str(value)

    return cleaned_metadata

@timer
def ingest_leaf_nodes(
    leaf_nodes: List[BaseNode], domain: str = "Douanes Benin"
) -> None:
    """Génère les embeddings et upsert les leaf_nodes dans Qdrant."""
    if not leaf_nodes:
        logger.warning("Aucun leaf_node à ingérer.")
        return

    embedder = EmbeddingModels(
        model_name=EMBEDDING_MODEL_NAME
    ).get_embeddings()
    if embedder is None:
        raise RuntimeError(
            "Impossible de charger le modèle d'embedding, ingestion annulée."
        )

    vector_store = get_vector_store_client()
    logger.info(
        f"Début de l'ingestion : {len(leaf_nodes)} leaf_node(s) pour le domaine '{domain}'"
    )

    for start in range(0, len(leaf_nodes), BATCH_SIZE_NODES):
        batch = leaf_nodes[start : start + BATCH_SIZE_NODES]
        texts = [node.get_content() for node in batch]

        vectors = embedder.embed_documents(texts)

        ids = []
        for node in batch:
            try:
                ids.append(str(uuid.UUID(node.node_id)))
            except ValueError:
                ids.append(str(uuid.uuid5(uuid.NAMESPACE_DNS, node.node_id)))

        metadatas = [
            _clean_metadata(node, domain, text)
            for node, text in zip(batch, texts)
        ]

        try:
            vector_store.upsert(ids=ids, vectors=vectors, metadatas=metadatas)
            logger.info(
                f"Batch {start // BATCH_SIZE_NODES + 1}/{(len(leaf_nodes) - 1) // BATCH_SIZE_NODES + 1} upserté."
            )
        except Exception as e:
            logger.error(f"Erreur lors de l'upsert du batch : {str(e)}")
            raise e

@timer
def process_batch(file_batch: List[Path], domain: str) -> None:
    logger.info("=== 1. Parsing du batch de documents ===")
    logger.info(f"Traitement de {len(file_batch)} document(s)")

    # 1. PARSING
    parser = ParserDocuments(file_paths=file_batch)
    docs_data = parser.parse_documents()

    if not docs_data:
        logger.warning("Aucun document n'a été parsé dans ce batch.")
        return

    # 2. CHUNKING
    logger.info("=== 2. Chunking hiérarchique ===")
    all_nodes, leaf_nodes, docstore = chuncking_hierachical(docs_data)
    logger.info(
        f"Nodes créés : {len(all_nodes)} | Leaf nodes : {len(leaf_nodes)}"
    )

    # 3. DOCSTORE
    logger.info("=== 3. Sauvegarde DocStore ===")
    DOCSTORE_FILE.parent.mkdir(parents=True, exist_ok=True)
    docstore.persist(str(DOCSTORE_FILE))
    logger.info(f"DocStore sauvegardé : {DOCSTORE_FILE}")

    # 4. EMBEDDINGS + QDRANT
    logger.info("=== 4. Embeddings + Qdrant ===")
    ingest_leaf_nodes(leaf_nodes, domain=domain)
    logger.info("Batch terminé avec succès.")


# PIPELINE COMPLET
# ============================================================

@timer
def run_ingestion_pipeline(
    domain: str = "Douanes Benin", batch_size: int = BATCH_SIZE_DOCS
) -> None:
    logger.info("🚀 Démarrage du pipeline d'ingestion")

    all_files = get_files()
    if not all_files:
        logger.warning("Aucun fichier trouvé.")
        return

    logger.info(f"{len(all_files)} document(s) trouvé(s).")

    state = load_ingestion_state()
    processed_documents = set(state.get("processed_documents", []))

    remaining_files = [
        path for path in all_files if path.name not in processed_documents
    ]

    logger.info(f"Documents déjà traités : {len(processed_documents)}")
    logger.info(f"Documents restants : {len(remaining_files)}")

    if not remaining_files:
        logger.info("🎉 Tous les documents ont déjà été traités.")
        return

    for start in range(0, len(remaining_files), batch_size):
        batch = remaining_files[start : start + batch_size]
        logger.info(f"\n📦 BATCH {start // batch_size + 1}")

        try:
            process_batch(file_batch=batch, domain=domain)

            for path in batch:
                processed_documents.add(path.name)

            state["processed_documents"] = sorted(list(processed_documents))
            save_ingestion_state(state)
            logger.info("✅ État d'ingestion sauvegardé.")

        except Exception as e:
            logger.error(
                f"❌ Échec du batch : {e}\nLes documents du batch ne seront pas marqués comme traités."
            )
            raise e

    logger.info("🏁 Pipeline d'ingestion terminé.")


if __name__ == "__main__":
    run_ingestion_pipeline(domain="Douanes Benin", batch_size=3)