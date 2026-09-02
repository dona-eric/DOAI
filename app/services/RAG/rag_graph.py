from typing import Any, Dict, List, Optional, TypedDict
from langgraph.graph import StateGraph, END
from app.core.loger import setup_logging
from app.services.retrievers.retrieving import Retriever
from app.utils.reranking import Reranker
from app.services.llms.endpoint import Generator

logger = setup_logging(__name__)

# Seuil de score minimal en dessous duquel les résultats rerankés sont rejetés
MIN_RERANK_SCORE = 0.25


class RAGState(TypedDict, total=False):
    query: str
    filters: Optional[Dict[str, Any]]
    candidates: List[Dict[str, Any]]
    reranked: List[Dict[str, Any]]
    answer: str
    sources: List[Dict[str, Any]]


# Singletons pour éviter le rechargement lourd des modèles en mémoire
_retriever = Retriever()
_reranker = Reranker()
_generator = Generator()


def retrieve_node(state: RAGState) -> Dict[str, Any]:
    candidates = _retriever.retrieve(
        query=state["query"],
        top_k=20,
        filters=state.get("filters"),
        fetch_parent_context=True,
    )
    return {"candidates": candidates}


def rerank_node(state: RAGState) -> Dict[str, Any]:
    reranked = _reranker.rerank(state["query"], state["candidates"], top_n=5)
    return {"reranked": reranked}


def generate_node(state: RAGState) -> Dict[str, Any]:
    answer = _generator.generate(state["query"], state["reranked"])
    
    # Extraction alignée avec la structure du Retriever corrigé
    sources = []
    for c in state["reranked"]:
        meta = c.get("metadata", {})
        sources.append({
            "source": meta.get("file_name", meta.get("source", "Inconnu")),
            "article_number": meta.get("article_number", "N/A"),
            "domain": meta.get("domain", "Général"),
            "score": round(c.get("rerank_score", c.get("score", 0.0)), 4),
        })

    return {"answer": answer, "sources": sources}


def no_context_node(state: RAGState) -> Dict[str, Any]:
    logger.warning(f"Aucun candidat pertinent retenu pour : '{state['query'][:60]}'")
    return {
        "answer": (
            "Je n'ai pas trouvé d'information suffisamment pertinente dans les documents "
            "disponibles pour répondre avec certitude à votre question."
        ),
        "sources": [],
    }


def route_after_retrieve(state: RAGState) -> str:
    """Achemine vers le reranking si des vecteurs candidats sont retournés."""
    return "rerank" if state.get("candidates") else "no_context"


def route_after_rerank(state: RAGState) -> str:
    """Filtre additionnel : vérifie si au moins un candidat dépasse le seuil de pertinence."""
    reranked = state.get("reranked", [])
    if not reranked:
        return "no_context"
    
    top_score = reranked[0].get("rerank_score", reranked[0].get("score", 0.0))
    if top_score < MIN_RERANK_SCORE:
        logger.info(f"Score Rerank top-1 trop faible ({top_score:.3f} < {MIN_RERANK_SCORE}). Bascule vers no_context.")
        return "no_context"
        
    return "generate"


def build_rag_graph():
    graph = StateGraph(RAGState)

    # Ajout des nœuds
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("rerank", rerank_node)
    graph.add_node("generate", generate_node)
    graph.add_node("no_context", no_context_node)

    # Point d'entrée
    graph.set_entry_point("retrieve")

    # Branchements conditionnels
    graph.add_conditional_edges(
        "retrieve",
        route_after_retrieve,
        {"rerank": "rerank", "no_context": "no_context"},
    )
    graph.add_conditional_edges(
        "rerank",
        route_after_rerank,
        {"generate": "generate", "no_context": "no_context"},
    )

    # Bords terminaux
    graph.add_edge("generate", END)
    graph.add_edge("no_context", END)

    return graph.compile()


# Instance compilée réutilisable par FastAPI/Streamlit
rag_app = build_rag_graph()