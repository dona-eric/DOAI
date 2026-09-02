from typing import Any, Dict, List
from openai import OpenAI

from app.core.config import IMOLE_API_KEY, IMOLE_BASE_URL, MODEL_IMOLE_DEFAULT
from app.core.loger import setup_logging

logger = setup_logging(__name__)

SYSTEM_PROMPT = (
    "Tu es un assistant spécialisé dans la réglementation douanière",
    "Tu es un agent ia qui repond dans un contexte béninois douanier",
    "Tu dois te comportement également comme un agent de la douane ou un commissaire agrée par la douane en charge des affaires portuaires, transports,logistique", 
    "portuaire du Bénin (Port Autonome de Cotonou, Douanes Béninoises). "
    "Tu dois repondre en français",
    "Réponds UNIQUEMENT à partir des extraits fournis dans le contexte ci-dessous.\n\n"
    "Règles strictes :\n"
    "1. Si le contexte ne permet pas de répondre avec certitude, dis-le clairement sans inventer.\n"
    "2. Cite systématiquement la source (nom du document) et le numéro d'article exact "
    "pour chaque affirmation importante.\n"
    "3. Adopte un ton professionnel, précis et juridiquement rigoureux."
)


class Generator:
    """
    Génère une réponse ancrée (grounded RAG) à partir des passages retenus,
    via l'API compatible OpenAI (Imole).
    """

    def __init__(self, model: str = MODEL_IMOLE_DEFAULT):
        self.client = OpenAI(api_key=IMOLE_API_KEY, base_url=IMOLE_BASE_URL)
        self.model = model

    @staticmethod
    def _build_context(chunks: List[Dict[str, Any]]) -> str:
        """
        Formate les blocs de contexte en combinant le texte parent (Article complet)
        et les métadonnées (nom du fichier, numéro d'article, domaine).
        """
        blocks = []
        for idx, chunk in enumerate(chunks, start=1):
            # Support rétrocompatible payload/metadata
            meta = chunk.get("metadata") or chunk.get("payload", {})
            
            source = meta.get("file_name", meta.get("source", "Source inconnue"))
            article = meta.get("article_number", "N/A")
            domain = meta.get("domain", "Général")

            # Utilisation prioritaire du texte parent complet, sinon fallback sur le texte brut
            text_content = chunk.get("parent_text") or chunk.get("text") or meta.get("text", "")

            header = f"[DOCUMENT {idx}: {source} | Domaine: {domain} | Article: {article}]"
            blocks.append(f"{header}\n{text_content.strip()}")

        return "\n\n---\n\n".join(blocks)

    def generate(self, query: str, chunks: List[Dict[str, Any]]) -> str:
        """
        Construit le prompt final et interroge le LLM via l'API Imole.
        """
        if not chunks:
            logger.warning("Aucun contexte disponible pour la génération.")
            return (
                "Je n'ai pas trouvé d'information pertinente dans les "
                "documents disponibles pour répondre à cette question."
            )

        context = self._build_context(chunks)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"CONTEXTE RÈGLEMENTAIRE :\n{context}\n\n"
                    f"QUESTION DU CLIENT :\n{query}"
                ),
            },
        ]

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.0,  # Déterminisme strict pour la précision juridique
            )
            
            answer = response.choices[0].message.content
            logger.info("Réponse RAG générée avec succès.")
            return answer

        except Exception as e:
            logger.error(f"Erreur lors de la génération avec le modèle {self.model} : {e}")
            return "Une erreur est survenue lors de la génération de la réponse règlementaire."