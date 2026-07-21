import json
from typing import Any

from langchain_core.documents import Document
from langchain_core.messages import BaseMessage

from src.llm.llm_factory import get_chat_model
from src.retrieval.retriever_factory import get_domain_vectorstore
from src.schemas.rag_response import RAGAgentResponse, RetrievedSource

DEFAULT_TOP_K = 4

class SpecializedRAGAgent:
    def __init__(
        self,
        department: str,
        agent_name: str,
        system_role: str,
        top_k: int = DEFAULT_TOP_K
    ) -> None:
        self.department = department
        self.agent_name = agent_name
        self.system_role = system_role
        self.top_k = top_k
    
    def retrieve_context(self, question: str) -> list[tuple[Document, float]]:
        vectorstore = get_domain_vectorstore(self.department)

        return vectorstore.similarity_search_with_score(
            query=question,
            k=self.top_k,
        )
    
    def build_context(self, retrieved_docs: list[tuple[Document, float]]) -> str:
        context_blocks= []

        for index, (document, score) in enumerate(retrieved_docs, start=1):
            metadata = document.metadata

            context_blocks.append(
                "\n".join(
                    [
                        f"[Source {index}]",
                        f"Chunk ID: {metadata.get('chunk_id', 'unknown')}",
                        f"Department: {metadata.get('department', self.department)}",
                        f"Source file: {metadata.get('source_file', 'unknown')}",
                        f"Page: {metadata.get('page')}",
                        f"Similarity score: {score}",
                        "Content:",
                        document.page_content,
                    ]
                )
            )
        
        return "\n\n".join(context_blocks)

    def build_prompt(self, question: str, context: str) -> str:
        return f"""
            You are {self.agent_name}, a specialized enterprise support RAG agent.

            Your domain is: {self.department}

            Role instructions:
            {self.system_role}

            You must answer using only the retrieved internal documentation context.
            If the context is not enough to answer safely, say that the available documentation does not contain enough information and recommend escalation to the appropriate team.

            Do not invent policies.
            Do not mention unsupported procedures.
            Do not expose implementation details.
            Do not say that you are using embeddings or vector databases.
            Keep the response professional, clear, and operational.

            Return only valid JSON with this structure:

            {{
            "user_question": "...",
            "department": "{self.department}",
            "agent_name": "{self.agent_name}",
            "answer": "...",
            "sources": [
                {{
                "chunk_id": "...",
                "department": "...",
                "source_file": "...",
                "source_path": "...",
                "page": null,
                "score": 0.0,
                "content_preview": "..."
                }}
            ]
            }}

            User question:
            {question}

            Retrieved internal documentation context:
            {context}
            """.strip()
    
    def build_scores(
        self,
        retrieved_docs: list[tuple[Document, float]],
    ) -> list[RetrievedSource]:
        sources = []

        for document, score in retrieved_docs:
            metadata = document.metadata

            sources.append(
                RetrievedSource(
                    chunk_id=metadata.get("chunk_id", "unknown"),
                    department=metadata.get("department", self.department),
                    source_file=metadata.get("source_file"),
                    source_path=metadata.get("source_path"),
                    page=metadata.get("page"),
                    score=float(score),
                    content_preview=document.page_content[:500],
                )
            )

        return sources
    
    def parse_model_response(
        self,
        model_response: BaseMessage,
        question: str,
        sources: list[RetrievedSource],
    ) -> RAGAgentResponse:
        raw_content = str(model_response.content).strip()

        try:
            parsed_content: dict[str, Any] = json.loads(raw_content)

            return RAGAgentResponse(
                user_question=parsed_content.get("user_question", question),
                department=parsed_content.get("department", self.department),
                agent_name=parsed_content.get("agent_name", self.agent_name),
                answer=parsed_content.get("answer", raw_content),
                sources=sources,
            )
        except json.JSONDecodeError:
            return RAGAgentResponse(
                user_question=question,
                department=self.department,
                agent_name=self.agent_name,
                answer=raw_content,
                sources=sources,
            )
        
    def answer(self, question: str) -> RAGAgentResponse:
        retrieved_docs = self.retrieve_context(question)
        context = self.build_context(retrieved_docs)
        prompt = self.build_prompt(question=question, context=context)
        sources = self.build_scores(retrieved_docs)

        model = get_chat_model()
        model_response = model.invoke(prompt)

        return self.parse_model_response(
            model_response=model_response,
            question=question,
            sources=sources,
        )


