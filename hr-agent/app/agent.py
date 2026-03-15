import os

import google.auth
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.apps.app import App
from google.adk.tools.agent_tool import AgentTool
from google.adk.planners import PlanReActPlanner
from google.adk.tools.retrieval.vertex_ai_rag_retrieval import (
    VertexAiRagRetrieval,
)
from .sub_agents.vacation_agent.agent import vacation_agent
from vertexai.preview import rag

import logging
import google.cloud.logging
from google.cloud.logging_v2.handlers import CloudLoggingHandler

# Initialize the Google Cloud Logging client
client = google.cloud.logging.Client()

# Create a Cloud Logging handler
handler = CloudLoggingHandler(client)

# Configure the root Python logger
logging.getLogger().setLevel(logging.INFO)
logging.getLogger().addHandler(handler)

logging.info("Cloud Logging initialized for ADK agent script.")
handler.close()

load_dotenv()

# Set up Google Cloud project and location
_, project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

# IMPORTANT: replace this with your corpus resource name
os.environ.setdefault(
    "RAG_CORPUS",
    f"projects/kevin-ai-playground/locations/asia-northeast3/ragCorpora/5148740273991319552",
)

# =========================================
# SPECIALIZED TOOLS
# =========================================

ask_vertex_retrieval = VertexAiRagRetrieval(
    name="retrieve_hr_rag",
    description=(
        "HR 업무중에서 휴가 규정에 대한 상세한 내용을 검색할 수 있다."
    ),
    rag_resources=[rag.RagResource(rag_corpus=os.environ.get("RAG_CORPUS"))],
    similarity_top_k=10,
    vector_distance_threshold=0.6,
)

# --- Root Agent ---
root_instructions = """
<OBJECTIVE_AND_PERSONA>
당신은 우리회사의 HR 담당자로서 특히 임직원들의 휴가 규정에 대한 상세한 답변을 할 수 있습니다. 
</OBJECTIVE_AND_PERSONA>

<INSTRUCTIONS>
사용 가능한 도구들
* vacation_agent: 남은 휴가에 대해서 물어보면 vacation_agent 에이전트를 통하여 답변합니다. 
* retrieve_hr_rag: 일반적인 휴가 규정, 규칙에 대한 문의라면 retrieve_hr_rag 툴을 사용하여 답변합니다. 
</INSTRUCTIONS>

<OUTPUT_FORMAT>
출력에는 다음과 같은 
1. 질문에 대한 답변
2. "연관 질문"이라는 제목으로 연관 질문 3개를 번호를 붙여서 만들어주세요.
</OUTPUT_FORMAT>
"""

root_agent = Agent(
    name="root_agent",
    model="gemini-2.5-flash",
    planner=PlanReActPlanner(),
    instruction=root_instructions,
    tools=[AgentTool(vacation_agent), ask_vertex_retrieval],
)

app = App(root_agent=root_agent, name="app")