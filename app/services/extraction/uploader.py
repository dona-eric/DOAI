import os
import sys
import pathlib
from app.core.loger import setup_logging
from PyPDF2 import PdfReader, PdfFileReader
import fitz , tempfile
from langchain_community.document_loaders import UnstructuredPDFLoader, PyMuPDFLoader, UnstructuredExcelLoader, UnstructuredWordDocumentLoader
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain.tools import tools
logger = setup_logging()



"""
fonction qui upload les fichiers (images, documents(pdf, txt, doc, docx etc..))

Pour les documents pdf, docx, on transforme chaque page en image pour faciliter l'extraction
"""

def upload_file(file_path):

    """
    Args:
        file_path(str): chemin complet du fichier
    Returns:
        string: th file is ready for extraction 
    """

    try:
        if 