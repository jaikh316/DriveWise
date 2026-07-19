from pydantic import BaseModel, Field
from typing import List

class SourceCitation(BaseModel):
    section: str = Field(..., description="The section name from the brochure used to answer the question, e.g., 'safety', 'engine_performance'.")
    page_number: int = Field(..., description="The exact page number of the brochure where the fact was found (1-indexed).")

class RAGResponse(BaseModel):
    answer: str = Field(
        ..., 
        description="The concise, plain-language answer to the user's question, strictly grounded in the provided context. If the context is insufficient or doesn't cover the answer, state that the information was not found in the brochure."
    )
    grounded: bool = Field(
        ..., 
        description="Must be set to True if the answer is directly supported by the context, and False if the context lacks information to answer the question."
    )
    sources: List[SourceCitation] = Field(
        default=[], 
        description="A list of unique source citations (section and page_number) used to construct the answer. Leave empty if grounded is False."
    )
