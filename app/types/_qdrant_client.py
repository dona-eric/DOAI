import os
import sys
from app.core.config import QDRANT_API_KEY, QDRANT_URL, PINECONE_API_KEY
from app.core.loger import setup_logging
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from pinecone import Pinecone, ServerlessSpec


logger = setup_logging()
logger.info("Client Qdrant initialisé avec succès")
class InitializeQdrantClient:

    """
    Initialise le client qdrant
    """
    def __init__(self, collection_name: str = "docmind"):
        self.client = QdrantClient(
            api_key=QDRANT_API_KEY, 
            url=QDRANT_URL,
            cloud_inference=True
        )
        self.collection_name = collection_name

    def _get_client(self):

        """
        Retourne le client qdrant
        """
        try:
            if not self.client:
                self.client = QdrantClient(
                    api_key=QDRANT_API_KEY, 
                    url=QDRANT_URL,
                    cloud_inference=True
                )
        except Exception as e:
            raise Exception(f"Erreur lors de l'initialisation du client qdrant: {str(e)}")
        return self.client

    def _create_vector_store(self, collection_name: str, ):

        """
        Crée une collection dans qdrant
        """
        try:
            if not self.client.collection_exists(collection_name):
                logger.info(f"Création de la collection {collection_name}")
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=1536, 
                        distance=Distance.COSINE
                    ),
                )
                logger.info(f"La collection {collection_name} a été créée avec succès")
        except Exception as e:
            raise Exception(f"Erreur lors de la création de la collection: {str(e)}")
        
    
# INITIALISATION CLIENT PINECONE

logger.info("Client Pinecone initialisé avec succès")

class PineconeClient:
    def __init__(self, index_name: str = "docmind"):
        self.client = Pinecone(
            api_key=PINECONE_API_KEY,
            environment="gcp-starter"
            )
        self.index_name = index_name


    def create_index(self):
        try:
            if not self.client.has_index(self.index_name):
                logger.info(f"Création de l'index {self.index_name}")
                self.client.create_index(
                    name=self.index_name,
                    dimension=1536,
                    metric="cosine",
                    spec= ServerlessSpec(
                        cloud="aws",
                        region="us-west-1"
                    )
                )
            logger.info(f"L'index {self.index_name} existe déjà")
        except Exception as e:
            raise Exception(f"Erreur lors de la création de l'index: {str(e)}")