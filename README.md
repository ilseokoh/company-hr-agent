# company-hr-agent

## 셋업

### Create ADK Project using the Agent Starter Pack

[Install uv](https://docs.astral.sh/uv/getting-started/installation/) 

```
uvx agent-starter-pack@0.39.2 create hr-agent
```

1. 1번 adk 선택
1. Deployment target: 1번 AI Agent Engine 선택
1. CI/CD runner: 2 Google Cloud Build 선택

```
cd hr-agent
```

```
hr-agent
├── GEMINI.md
├── Makefile
├── README.md
├── app
│   ├── __init__.py
│   ├── agent.py
│   ├── agent_engine_app.py
│   └── app_utils
│       ├── deploy.py
│       ├── telemetry.py
│       └── typing.py
├── deployment
│   ├── README.md
│   └── terraform
│       ├── apis.tf
│       ├── build_triggers.tf
│       ├── dev
│       │   ├── apis.tf
│       │   ├── iam.tf
│       │   ├── outputs.tf
│       │   ├── providers.tf
│       │   ├── service.tf
│       │   ├── service_outputs.tf
│       │   ├── storage.tf
│       │   ├── telemetry.tf
│       │   ├── telemetry_outputs.tf
│       │   ├── variables.tf
│       │   └── vars
│       │       └── env.tfvars
│       ├── github.tf
│       ├── iam.tf
│       ├── locals.tf
│       ├── outputs.tf
│       ├── providers.tf
│       ├── service.tf
│       ├── service_accounts.tf
│       ├── service_outputs.tf
│       ├── sql
│       │   └── completions.sql
│       ├── storage.tf
│       ├── telemetry.tf
│       ├── telemetry_outputs.tf
│       ├── variables.tf
│       └── vars
│           └── env.tfvars
├── deployment_metadata.json
├── notebooks
│   ├── adk_app_testing.ipynb
│   └── evaluating_adk_agent.ipynb
├── pyproject.toml
├── tests
│   ├── eval
│   │   ├── eval_config.json
│   │   └── evalsets
│   │       ├── README.md
│   │       └── basic.evalset.json
│   ├── integration
│   │   ├── test_agent.py
│   │   └── test_agent_engine_app.py
│   ├── load_test
│   │   ├── README.md
│   │   └── load_test.py
│   └── unit
│       └── test_dummy.py
└── uv.lock
```

## Install dependencies and launch the local playground 

```
make install && make playground
```

### Test

1. 브라우저에서 [http://127.0.0.1:8501](http://127.0.0.1:8501) 접속 
1. app 을 선택한다
1. 아래 질문으로 테스트 
    ```
    What's the weather in San Francisco?
    ```
1. Ctrl+c 로 빠져나온다. 

## 문서 준비 

Google Cloud Storage 에 버킷을 만들고 관련 파일을 업로드 한다. 

* [GCS 버킷 만들기](https://docs.cloud.google.com/storage/docs/creating-buckets#create-bucket)
* [버킷에 파일 업로드](https://docs.cloud.google.com/storage/docs/uploading-objects#uploading-an-object)


## Set up the RAG 

1. In the Google Cloud console, navigate to Vertex AI > RAG Engine.
1. Click Create corpus.
1. Configure the corpus as follows:
    * Region: asin-northeast3
    * Corpus name: hr-contents
    * For Data, click Select from Google Cloud Storage.
1. Click Browse, select the BUCKET bucket, and click Select.
1. Expand Advanced options and set the following:
    * Parser: LLM Parser
    * Model: Gemini 2.5 Flash
    * Click Continue.
1. For the Configure vector store step, select Text Multilingual Embedding 002 as the embedding model.
1. Select RagManaged Cloud Spanner as the vector database.
1. Click Create corpus in the top left.

Corpus creation can take 3-5 minutes to complete.

## Update the agent's code for RAG

app/agent.py 코드를 아래와 같이 수정한다. 

```
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
```
### RAG_CORPUS 환경 변수 설정

1. In the Google Cloud console, navigate to Vertex AI > RAG Engine.
1. Open the **hr-contents** corpus details page.
1. Copy the Resource Name (it has the format: projects/your-project/locations/your-location/ragCorpora/your-corpus-id) to the clipboard.
1. open the file app/agent.py. RAG_CORPUS 를 업데이트 해준다. 

### 테스트 

1. **make playground** 를 실행하고 브라우저에서 [http://127.0.0.1:8501](http://127.0.0.1:8501) 접속
1. 문서에 있는 내용으로 질문을 만들어서 테스트 

## API 호출 Tool 

## Gemini CLI 를 사용할 때 ADK 문서를 사용하는 방법 

### Gemini CLI 사용

```
export GOOGLE_CLOUD_PROJECT=kevin-ai-playground
export GOOGLE_CLOUD_LOCATION=asia-northeast3
gemini
```