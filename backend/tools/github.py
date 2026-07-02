import httpx

from config import settings


def get_github_activity() -> list[dict]:
    url = f"https://api.github.com/users/{settings.github_username}/events?per_page=10"
    try:
        resp = httpx.get(url, timeout=10)
        resp.raise_for_status()
        events = resp.json()
    except Exception as e:
        return [{"error": f"Failed to fetch GitHub activity: {e}"}]

    results = []
    for event in events[:10]:
        event_type = event.get("type", "Unknown")
        repo = event.get("repo", {}).get("name", "unknown")
        created_at = event.get("created_at", "")
        payload = event.get("payload", {})

        description = ""
        if event_type == "PushEvent":
            commits = payload.get("commits", [])
            commit_msgs = [c.get("message", "").split("\n")[0] for c in commits[:3]]
            description = f"Pushed {len(commits)} commit(s): {'; '.join(commit_msgs)}"
        elif event_type == "CreateEvent":
            ref_type = payload.get("ref_type", "branch")
            ref = payload.get("ref", "")
            description = f"Created {ref_type} '{ref}'"
        elif event_type == "IssuesEvent":
            action = payload.get("action", "unknown")
            issue_title = payload.get("issue", {}).get("title", "")
            description = f"{action.capitalize()} issue: {issue_title}"
        elif event_type == "PullRequestEvent":
            action = payload.get("action", "unknown")
            pr_title = payload.get("pull_request", {}).get("title", "")
            description = f"{action.capitalize()} PR: {pr_title}"
        elif event_type == "WatchEvent":
            description = "Starred repository"
        elif event_type == "ForkEvent":
            description = f"Forked to {payload.get('forkee', {}).get('full_name', '')}"
        else:
            description = event_type

        results.append({
            "type": event_type,
            "repo": repo,
            "date": created_at,
            "description": description,
        })

    return results if results else [{"message": "No recent GitHub activity found."}]
