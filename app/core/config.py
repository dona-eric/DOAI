from sympy.parsing.sympy_parser import TOKEN
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
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
TOKEN_HUGGINGFACE = os.getenv("HUGGINGFACE_TOKEN")
REPO_ID="Qwen/Qwen3.8-2.4T-A95B"
IMOLE_API_KEY = os.getenv("IMOLE_API_KEY")
IMOLE_BASE_URL = "https://api.imole.app/v1"
MODEL_IMOLE_DEFAULT="gpt-5.6-luna"
EMBEDDING_DIMENSION =384
EMBEDDING_MODEL_NAME="sentence-transformers/all-mpnet-base-v2"
VECTOR_PROVIDER="qdrant"