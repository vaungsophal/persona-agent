import uuid
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from models import ChatRequest, ChatResponse, ContactRequest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="PO Agent API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions: dict[str, dict] = {}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    from agent import SessionMemory, load_system_prompt, build_bedrock_client, call_claude_with_tools
    from tools.search import search_projects, get_project_details, get_bio, get_skills, get_experience
    from tools.github import get_github_activity
    from tools.contact import contact_po

    session_id = req.session_id or str(uuid.uuid4())

    if session_id not in sessions:
        sessions[session_id] = {
            "memory": SessionMemory(),
            "messages": [],
        }

    session = sessions[session_id]
    memory = session["memory"]

    if not session["messages"]:
        memory.visitor_type = memory.infer_visitor_type(req.message)

    system_prompt = load_system_prompt()
    if memory.visitor_type != "unknown":
        system_prompt += f"\n\n## Visitor context\n{memory.system_prompt_extra()}"

    bedrock = build_bedrock_client()

    session["messages"].append({"role": "user", "content": [{"type": "text", "text": req.message}]})

    tool_implementations = {
        "search_projects": search_projects,
        "get_project_details": get_project_details,
        "get_github_activity": get_github_activity,
        "contact_po": contact_po,
    }

    try:
        reply = call_claude_with_tools(
            bedrock=bedrock,
            system_prompt=system_prompt,
            messages=session["messages"],
            tool_implementations=tool_implementations,
        )
    except Exception as e:
        logger.error(f"Agent error: {e}", exc_info=True)
        reply = "I'm sorry, I hit an internal error. Please try again or reach out directly."

    session["messages"].append({"role": "assistant", "content": [{"type": "text", "text": reply}]})

    if len(session["messages"]) > 40:
        session["messages"] = session["messages"][-40:]

    return ChatResponse(reply=reply, session_id=session_id)


@app.post("/contact", response_model=dict)
async def contact(req: ContactRequest):
    from tools.contact import contact_po
    result = contact_po(req.visitor_name, req.message, req.contact_info)
    return result
