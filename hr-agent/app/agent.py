import os

import google.auth
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.apps.app import App
from google.adk.tools.agent_tool import AgentTool
from google.adk.planners import PlanReActPlanner

from .sub_agents.vacation_agent.agent import vacation_agent
from .sub_agents.ask_vertex_agent.agent import ask_vertex_agent

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

# =========================================
# SPECIALIZED TOOLS
# =========================================


# --- Root Agent ---
root_instructions = """
<OBJECTIVE_AND_PERSONA>
당신은 우리회사의 HR 담당자로서 특히 임직원들의 휴가 규정에 대한 상세한 답변을 할 수 있습니다. 
</OBJECTIVE_AND_PERSONA>

<INSTRUCTIONS>
* 휴가를 신청하는 요청이 오면 사용자로부터 시작일, 종료일, 사유를 받아서 vacation_agent 에이전트를 통하여 답변합니다. 
* 남은 휴가에 대해서 물어보면 vacation_agent 에이전트를 통하여 답변합니다. 
* 우리회사의 휴가 규정에 대해서 물어보면 ask_vertex_agent 에이전트를 통하여 답변합니다. 

사용 가능한 도구들
* vacation_agent: 남은 휴가에 대해서 물어보거나 휴가 신청을 하려면 vacation_agent 에이전트를 통하여 답변합니다. 
* ask_vertex_agent: 일반적인 휴가 규정, 규칙에 대한 문의라면 ask_vertex_agent 에이전트를 통하여 답변합니다. 
</INSTRUCTIONS>

<OUTPUT_FORMAT>
출력에는 다음과 같은 
1. 질문에 대한 답변
2. 휴가 규정에 대해서 물어보는 경우에만 "연관 질문"이라는 제목으로 연관 질문 3개를 번호를 붙여서 만들어주세요.
</OUTPUT_FORMAT>
"""

root_agent = Agent(
    name="root_agent",
    model="gemini-2.5-flash",
    planner=PlanReActPlanner(),
    instruction=root_instructions,
    tools=[AgentTool(vacation_agent), AgentTool(ask_vertex_agent)],
)

app = App(root_agent=root_agent, name="app")