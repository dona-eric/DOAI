from app.core.config import LLAMA_PARSE_API_KEY
from genericpath import exists
import os
import time
from pathlib import Path
from typing import List, Optional
from app.core.loger import setup_logging
from app.services.processing.loader import get_files
from app.types._base_client import get_llama_cloud_client

logger = setup_logging()

"""
Cette fonction ou class de fonction analyse les differents documents
selon leurs types et leurs contenus respectifs et leurs classifier par
categorie pour un travail de vectorisation et de stockage dans qdrant.
"""

class DocumentParser:
    
    """
    Cette fonction ou class de fonction analyse les differents documents
    selon leurs types et leurs contenus respectifs et leurs parse en utilisant llama
    cloud.
    """

    def __init__(self, file_paths: Optional[List[str]] = None):
        self.client = get_llama_cloud_client(api_key=LLAMA_PARSE_API_KEY)
        
        # utilise les fichiers passer en paramètres ou utilise les fichiers de get_files()
        self.file_paths : List[Path] = file_paths if file_paths is not None else get_files()

        logger.info(f"DocumentParser intiliaze successfully with {len(self.file_paths)} documents")
        

    def parse_documents(self):
        """
        Parcourt les 12+ documents, 
        les envoie à LlamaParse et récupère le Markdown structuré.
        """
        total_files = len(self.file_paths)
        if total_files == 0:
            logger.warning("Aucun fichier trouvé à parser.")
            return []

        parsed_results = []

        for idx, file_path in enumerate(self.file_paths, start=1):
            logger.info(f"Traitement du fichier [{idx}/{total_files}] : {file_path.name}")

            try:
                # 1. Téléversement
                logger.info(f"Téléversement du fichier {file_path.name}...")
                with open(file_path, "rb") as f:
                    file_obj = self.client.files.create(
                        file=(file_path.name, f),
                        purpose="parse"
                    )

                logger.info(f"Fichier {file_path.name} uploadé avec succès")

                # 2. Création du job de parsing
                # tier="agentic" offre la meilleure extraction pour les PDF/DOCX complexes
                result = self.client.parsing.parse(
                    file_id=file_obj.id,
                    tier="agentic",
                    version="latest",
                    expand=["markdown_full", "text_full"],
                )

                # 3. Extraction des contenus
                markdown_text = result.markdown_full or ""
                raw_text = result.text_full or ""

                result_dict = {
                    "file_name": str(file_path.name),
                    "file_path": str(file_path),
                    "file_extension": file_path.suffix.lower(),
                    "file_id": str(file_obj.id),
                    "markdown": str(markdown_text),
                    "text": str(raw_text),
                }

                parsed_results.append(result_dict)

                logger.info(
                    f" Parsing réussi pour {file_path.name} "
                    f"({len(markdown_text)} chars markdown, {len(raw_text)} chars texte)."
                )

            except Exception as e:
                logger.error(f" Erreur lors du traitement de {file_path.name} : {str(e)}", exc_info=True)

        logger.info(f"Fin du traitement. {len(parsed_results)}/{total_files} documents parsés avec succès.")
        return parsed_results

if __name__ == "__main__":
    # Test d'exécution directe
    parser = DocumentParser()
    results = parser.parse_documents()
    
    print("\n================ RÉSUMÉ DU PARSING ================")
    for res in results:
        # Debug de sécurité si res n'est pas un dictionnaire
        if isinstance(res, tuple):
            res = res[0]
            
        file_name = res.get("file_name", "Inconnu")
        file_ext = res.get("file_extension", "")
        md_content = res.get("markdown", "")
        
        print(f"• {file_name} ({file_ext}) -> {len(md_content)} caractères extraits.")
    
    print("===================================================\n")