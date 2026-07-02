import json
import boto3
from botocore.config import Config as BotoConfig
from typing import Callable

from config import settings


TOOL_DEFINITIONS = [
    {
        "name": "search_projects",
        "description": "Search portfolio projects by keyword. Use this before get_project_details.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search keywords"}
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_project_details",
        "description": "Get full details of a specific portfolio project.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Project name (e.g. screenwise, callaflorist)"}
            },
            "required": ["name"],
        },
    },
    {
        "name": "get_github_activity",
        "description": "Fetch Vaungsophal's recent public GitHub activity. Use when asked about recent work or current projects.",
        "input_schema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "contact_po",
        "description": "Send a message to Vaungsophal via Telegram. Use when a visitor wants to reach out, hire, collaborate, or ask something you can't answer.",
        "input_schema": {
            "type": "object",
            "properties": {
                "visitor_name": {"type": "string", "description": "Visitor's name"},
                "message": {"type": "string", "description": "Message content"},
                "contact_info": {"type": "string", "description": "How to reach the visitor back (email, LinkedIn, etc.)"},
            },
            "required": ["visitor_name", "message", "contact_info"],
        },
    },
]


class SessionMemory:
    def __init__(self):
        self.visitor_type: str = "unknown"
        self.message_history: list[dict] = []

    def infer_visitor_type(self, message: str) -> str:
        msg_lower = message.lower()
        hiring_keywords = ["hire", "recruit", "position", "role", "job", "opening", "interview"]
        client_keywords = ["project", "contract", "freelance", "build", "develop", "need a", "looking for"]
        dev_keywords = ["architecture", "stack", "how did you", "code", "api", "deploy", "github"]

        hiring_score = sum(1 for w in hiring_keywords if w in msg_lower)
        client_score = sum(1 for w in client_keywords if w in msg_lower)
        dev_score = sum(1 for w in dev_keywords if w in msg_lower)

        if hiring_score > client_score and hiring_score > dev_score:
            return "recruiter"
        elif client_score > dev_score:
            return "potential_client"
        elif dev_score > 0:
            return "fellow_developer"
        return "unknown"

    def system_prompt_extra(self) -> str:
        extras = {
            "recruiter": "This visitor appears to be a recruiter. Emphasize outcomes and impact.",
            "potential_client": "This visitor appears to be a potential client. Emphasize services and reliability.",
            "fellow_developer": "This visitor appears to be a fellow developer. Feel free to share architecture details.",
            "unknown": "The visitor type is unclear. Respond naturally.",
        }
        return extras.get(self.visitor_type, "")


def load_system_prompt() -> str:
    with open("backend/prompts/system.md", "r", encoding="utf-8") as f:
        return f.read()


def build_bedrock_client():
    return boto3.client(
        "bedrock-runtime",
        region_name=settings.aws_region,
        config=BotoConfig(
            retries={"max_attempts": 3, "mode": "adaptive"},
            read_timeout=60,
        ),
    )


def call_claude_with_tools(
    bedrock,
    system_prompt: str,
    messages: list[dict],
    tool_implementations: dict[str, Callable],
    max_tool_rounds: int = 10,
) -> str:
    for _ in range(max_tool_rounds):
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2048,
            "system": system_prompt,
            "messages": messages,
            "tools": TOOL_DEFINITIONS,
        }

        response = bedrock.invoke_model(
            modelId=settings.bedrock_model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(body),
        )

        response_body = json.loads(response["body"].read())
        content_blocks = response_body["content"]

        assistant_content = []
        tool_calls = []

        for block in content_blocks:
            if block["type"] == "text":
                assistant_content.append({"type": "text", "text": block["text"]})
            elif block["type"] == "tool_use":
                tool_name = block["name"]
                tool_input = block.get("input", {})
                tool_use_id = block["id"]
                tool_calls.append((tool_use_id, tool_name, tool_input))
                assistant_content.append(block)

        messages.append({"role": "assistant", "content": assistant_content})

        if not tool_calls:
            final_text = ""
            for block in content_blocks:
                if block["type"] == "text":
                    final_text += block["text"]
            return final_text

        for tool_use_id, tool_name, tool_input in tool_calls:
            if tool_name in tool_implementations:
                try:
                    result = tool_implementations[tool_name](**tool_input)
                    result_str = json.dumps(result, ensure_ascii=False)
                except Exception as e:
                    result_str = json.dumps({"error": str(e)})
            else:
                result_str = json.dumps({"error": f"Unknown tool: {tool_name}"})

            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": result_str,
                    }
                ],
            })

    return "I've processed your request but hit the complexity limit. Let me know if you need more detail."
