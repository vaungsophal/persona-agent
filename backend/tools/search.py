import json
import os
from pathlib import Path

CONTENT_DIR = Path(__file__).resolve().parent.parent / "content"
PROJECTS_DIR = CONTENT_DIR / "projects"


def _read_markdown(filepath: Path) -> str:
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def _all_project_names() -> list[str]:
    if not PROJECTS_DIR.exists():
        return []
    return [f.stem for f in PROJECTS_DIR.iterdir() if f.suffix == ".md"]


def _project_summary(name: str) -> str | None:
    filepath = PROJECTS_DIR / f"{name}.md"
    if not filepath.exists():
        return None

    content = _read_markdown(filepath)
    lines = content.split("\n")
    title = ""
    problem = ""
    stack = ""
    for i, line in enumerate(lines):
        if line.startswith("# "):
            title = line.lstrip("# ").strip()
        if line.startswith("**Problem:**") and not problem:
            problem = line.replace("**Problem:**", "").strip()
        if line.startswith("**Stack:**") and not stack:
            stack = line.replace("**Stack:**", "").strip()

    summary = f"{title}: {problem} | Stack: {stack}" if problem else title
    return summary


def search_projects(query: str) -> list[dict]:
    query_lower = query.lower()
    results = []
    for name in _all_project_names():
        filepath = PROJECTS_DIR / f"{name}.md"
        content = _read_markdown(filepath).lower()
        if query_lower in content:
            summary = _project_summary(name)
            if summary:
                results.append({"name": name, "summary": summary})
    return results if results else [{"message": f"No projects found matching '{query}'."}]


def get_project_details(name: str) -> dict:
    filepath = PROJECTS_DIR / f"{name}.md"
    if not filepath.exists():
        available = _all_project_names()
        return {"error": f"Project '{name}' not found.", "available_projects": available}

    content = _read_markdown(filepath)
    return {"name": name, "content": content}


def get_bio() -> str:
    bio_path = CONTENT_DIR / "bio.md"
    if bio_path.exists():
        return _read_markdown(bio_path)
    return ""


def get_skills() -> dict:
    skills_path = CONTENT_DIR / "skills.json"
    if skills_path.exists():
        with open(skills_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def get_experience() -> list:
    exp_path = CONTENT_DIR / "experience.json"
    if exp_path.exists():
        with open(exp_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def get_certifications() -> list:
    cert_path = CONTENT_DIR / "certifications.json"
    if cert_path.exists():
        with open(cert_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []
