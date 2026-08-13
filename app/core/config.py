import os
import pathlib
import requests
import dotenv


### chargement des données keys de l'environnement virtual
dotenv.load_dotenv()

# KEYS LLAMA CLOUD

LLAMA_PARSE_API_KEY = os.getenv("LLAMA_PARSE_API_KEY")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_URL = "https://9825a19f-edf3-46a3-b7b7-cbe118083f9e.us-west-1-0.aws.cloud.qdrant.io"
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")