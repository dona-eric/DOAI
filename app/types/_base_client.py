from __future__ import annotations
import os
import sys
import httpx
from typing import Any, Dict, Optional, DefaultDict,Deque, Generator, List, Union
from app.core.loger import setup_logging
from pathlib import Path
from typing import IO
import time
import json
import uuid
import dotenv
from app.core.config import LLAMA_PARSE_API_KEY
from llama_cloud import LlamaCloud

dotenv.load_dotenv()
logger = setup_logging(__name__)

custom_httpx_client = httpx.Client(timeout=httpx.Timeout(300.0, connect=60.0))


def get_llama_cloud_client(
    api_key: str = LLAMA_PARSE_API_KEY
):
    """Retourne le client LlamaCloud"""

    client = LlamaCloud(
        api_key=api_key,
        http_client=custom_httpx_client
    )
    logger.info(f"Client LlamaCloud intialisé avec succès {api_key}")
    return client