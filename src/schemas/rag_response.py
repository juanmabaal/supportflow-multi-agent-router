from pydantic import BaseModel, Field

class RetrievedSource(BaseModel):
    chunk_id: str
    department: str
    source_file: str | None = None
    source_path: str | None = None
    page: int | None = None
    score: float | None = None
    content_preview: str

class RAGAgentResponse(BaseModel):
    user_question: str
    department: str
    agent_name: str
    answer: str
    sources: list[RetrievedSource] = Field(default_factory=list)