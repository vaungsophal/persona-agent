from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from models import ChatRequest, ChatResponse, ContactRequest

app = FastAPI(title="PO Agent API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    return ChatResponse(reply="Not implemented yet.", session_id=req.session_id or "default")


@app.post("/contact", response_model=dict)
async def contact(req: ContactRequest):
    return {"status": "received"}
