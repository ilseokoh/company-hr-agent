import os

import google.auth
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.apps.app import App
from google.adk.tools import AgentTool, google_search
from google.adk.tools.retrieval.vertex_ai_rag_retrieval import (
    VertexAiRagRetrieval,
)
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
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "asia-northeast3")
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

# =========================================
# AGENT DEFINITIONS
# =========================================

# 2. 오늘을 기준으로 남이 있는 휴가를 get_balance_as_of_today 툴을 사용하여 가져 옵니다.
# 3. 남아 있는 휴가를 바탕으로 


# --- Root Agent ---
root_instructions = """
<OBJECTIVE_AND_PERSONA>
당신은 우리회사의 HR 담당자로서 특히 임직원들의 휴가 규정에 대한 상세한 답변을 할 수 있습니다. 
</OBJECTIVE_AND_PERSONA>

<INSTRUCTIONS>
올바른 답변을 위해서 아래 단계를 따라주세요.
1. 일반적인 휴가 규정, 규칙에 대한 문의라면 retrieve_hr_rag 툴을 사용하여 답변합니다. 
2. 질문과 연관된 추가 질문 3개를 만들어주세요. 
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
    instruction=root_instructions,
    tools=[ask_vertex_retrieval],
)

app = App(root_agent=root_agent, name="app")