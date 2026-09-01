from typing import Optional

from app.core.loger import setup_logging
from app.core.config import TOKEN_HUGGINGFACE
from langchain_huggingface import HuggingFaceEmbeddings
from app.services.processing.parser import timer
logger = setup_logging(__name__)

DEFAULT_PROVIDER = "huggingface"
DEFAULT_CACHE_FOLDER = "./cache"


class EmbeddingModels:
    """
    Charge et met en cache un modele d'embedding selon le provider demande.
    Pour l'instant, seul HuggingFace (local, via sentence-transformers) est
    supporte.
    """

    def __init__(self, model_name: str, provider: str = DEFAULT_PROVIDER):
        self.model_name = model_name
        self.provider = (provider or DEFAULT_PROVIDER).lower()
        self._embeddings: Optional[HuggingFaceEmbeddings] = None  # cache d'instance

    @timer
    def get_embeddings(self) -> Optional[HuggingFaceEmbeddings]:
        if self._embeddings is not None:
            return self._embeddings

        try:
            if self.provider == "huggingface":
                self._embeddings = HuggingFaceEmbeddings(
                    model_name=self.model_name,
                    cache_folder=DEFAULT_CACHE_FOLDER,
                    model_kwargs={
                        "device": "cpu",  # passe a "cuda" si un GPU est disponible
                    },
                    encode_kwargs={
                        "normalize_embeddings": True,
                    },
                )
                logger.info(f"Embedding HuggingFace '{self.model_name}' charge avec succes")
                return self._embeddings

            logger.error(
                f"Provider d'embedding non supporte : '{self.provider}' "
                f"(seul 'huggingface' est implemente pour l'instant)"
            )
            return None

        except Exception as e:
            logger.error(f"Erreur lors du chargement de l'embedding : {e}")
            return None