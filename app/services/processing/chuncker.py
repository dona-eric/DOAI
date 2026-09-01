from app.core.loger import setup_logging
from typing import List, Dict, Optional, Tuple, Union
from app.services.processing.parser import ParserDocuments
from llama_index.core.node_parser import HierarchicalNodeParser, get_leaf_nodes
from llama_index.core import Document as LlamaDocument
from llama_index.core.schema import BaseNode
from llama_index.core.storage.docstore import SimpleDocumentStore

logger = setup_logging(__name__)

"""
Ici je teste dans un premier temps la technique de segmentation Hierachique
car les données sont des rapports, des articles avec des secrtions, des codes et lois.
"""

def chuncking_hierachical(
    docs_data: Union[Dict[str, str], List[LlamaDocument]],
    chunk_sizes: Optional[List[int]] = None)-> Tuple[List[BaseNode], List[BaseNode], SimpleDocumentStore]:

    if chunk_sizes is None:
        chunk_sizes=[512, 256, 128]
        
    llama_docs: List[LlamaDocument] = []

    if isinstance (docs_data, dict):
        for file_name, file_data in docs_data.items():
            if file_data.strip():
                doc = LlamaDocument(
                    text=file_data,
                    extra_info={"file_name": file_name, "source": file_name}
                )
                llama_docs.append(doc)
    else:
        llama_docs = docs_data      

    if not llama_docs:
        logger.warning("Aucun document a chunker.")
        return [], [], SimpleDocumentStore()

    logger.info(f"Chunking de {len(llama_docs)} document(s) avec sizes={chunk_sizes}...")

    nodes = HierarchicalNodeParser.from_defaults(
        chunk_sizes=chunk_sizes
    )
    all_nodes = nodes.get_nodes_from_documents(llama_docs)
    leaf_nodes = get_leaf_nodes(all_nodes)

    docstore = SimpleDocumentStore()
    docstore.add_documents(all_nodes)

    return all_nodes, leaf_nodes, docstore
