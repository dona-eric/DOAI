import sys
from pathlib import Path
from app.core.loger import setup_logging

logger = setup_logging(__name__)

data = Path(__file__).resolve().parents[3] / "data"

def get_files():

    logger.info("Initialisation de la recherche des fichiers... ")
    files = []

    for ext in (".pdf", ".docx", ".txt", ".md", ".xlsx"):
        files.extend(list(data.rglob(f"*{ext}")))

    return sorted(files)