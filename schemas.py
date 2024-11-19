from pydantic import BaseModel
from typing import List

class Document(BaseModel):
    documents: List[str]

class Query(BaseModel):
    query: str
