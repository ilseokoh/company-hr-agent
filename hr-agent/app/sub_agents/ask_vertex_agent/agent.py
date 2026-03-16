import os

from google.adk.tools.retrieval.vertex_ai_rag_retrieval import (
    VertexAiRagRetrieval,
)
from vertexai.preview import rag
from google.adk.agents import Agent

# your corpus resource name
os.environ.setdefault(
    "RAG_CORPUS",
    f"projects/kevin-ai-playground/locations/asia-northeast3/ragCorpora/5148740273991319552",
)

ask_vertex_retrieval = VertexAiRagRetrieval(
    name="retrieve_hr_rag",
    description=(
        "HR 업무중에서 휴가 규정에 대한 상세한 내용을 검색할 수 있다."
    ),
    rag_resources=[rag.RagResource(rag_corpus=os.environ.get("RAG_CORPUS"))],
    similarity_top_k=10,
    vector_distance_threshold=0.6,
)

ask_vertex_agent = Agent(
    name="ask_vertex_agent",
    model="gemini-2.5-flash",
    description="당신은 우리회사의 HR 담당자로서 특히 임직원들의 휴가 규정에 대한 상세한 답변을 할 수 있습니다. ",
    instruction="""
    당신은 우리회사의 HR 담당자입니다. 

    일반적인 휴가 규정, 규칙에 대한 문의에 대해서 ask_vertex_retrieval 툴을 사용하여 답변합니다. 
    """,
    tools=[ask_vertex_retrieval]
)