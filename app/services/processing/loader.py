import sys
from pathlib import Path
import os
from typing import List
from app.core.loger import setup_logging

logger = setup_logging()

logger.info("CHARGEMENT DES DOCUMENTS-ARTICLES-LAWER-CODE (PDF, DOCX)")


data = Path(__file__).resolve().parents[3] / "data"

def get_files():

    logger.info("Initialisation de la recherche des fichiers... ")
    files = []

    for ext in (".pdf", ".docx", ".txt", ".md", ".xlsx", ".png", ".jpg"):
        files.extend(list(data.rglob(f"*{ext}")))

    return sorted(files)

if __name__=="__main__":
    files = get_files()
    logger.info(f"Nombres de fichiers trouvés: {len(files)}")
    logger.info("Fichiers trouvés: ")
    logger.info(files)

        