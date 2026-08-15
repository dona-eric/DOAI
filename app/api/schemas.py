from pydantic import BaseModel, Field
from typing import List, Optional

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=3, description="Question de l'utilisateur")
    domain: Optional[str] = Field(None, description="Filtre optionnel, ex: 'Douanes Benin'")
    level: Optional[str] = Field(None, description="Filtre optionnel : article, section, table, page")


class SourceItem(BaseModel):
    source: Optional[str] = None
    article_number: Optional[str] = None
    score: Optional[float] = None


class QueryResponse(BaseModel):
    query: str
    answer: str
    sources: List[SourceItem]