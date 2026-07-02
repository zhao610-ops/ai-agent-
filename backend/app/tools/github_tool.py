from datetime import datetime, timedelta, timezone

import requests


MOCK_REPOS = [
    ("langchain-ai/langgraph", "构建可控的有状态 Agent 工作流", 11800, 2100, "Python", ["agent", "workflow"]),
    ("microsoft/autogen", "多 Agent 对话与协作框架", 39000, 5900, "Python", ["multi-agent", "llm"]),
    ("crewAIInc/crewAI", "面向角色协作的多 Agent 框架", 33000, 4400, "Python", ["agents", "automation"]),
    ("browser-use/browser-use", "让 Agent 控制浏览器", 42000, 4800, "Python", ["browser-agent", "automation"]),
    ("modelcontextprotocol/python-sdk", "MCP Python SDK", 16000, 2200, "Python", ["mcp", "tools"]),
    ("openai/openai-agents-python", "轻量级 Agent 开发框架", 12000, 1800, "Python", ["agents", "tool-calling"]),
    ("geekan/MetaGPT", "多 Agent 软件开发框架", 49000, 6100, "Python", ["multi-agent", "software"]),
    ("Significant-Gravitas/AutoGPT", "自主 Agent 平台", 170000, 45000, "Python", ["autonomous-agent"]),
    ("run-llama/llama_index", "面向数据的 Agent 与 RAG 框架", 39000, 5600, "Python", ["rag", "agents"]),
    ("camel-ai/camel", "可扩展多 Agent 社会框架", 13000, 1500, "Python", ["multi-agent"]),
]


class GithubTool:
    def __init__(self, token: str = "", timeout: int = 20):
        self.token = token
        self.timeout = timeout

    def search(self, limit: int = 10) -> list[dict]:
        since = (datetime.now(timezone.utc) - timedelta(days=365 * 3)).date().isoformat()
        headers = {"Accept": "application/vnd.github+json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        response = requests.get(
            "https://api.github.com/search/repositories",
            params={"q": f'("AI agent" OR multi-agent OR topic:ai-agents) pushed:>{since}', "sort": "stars", "order": "desc", "per_page": limit},
            headers=headers,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return [self._normalize(item) for item in response.json().get("items", [])]

    @staticmethod
    def _normalize(item: dict) -> dict:
        return {
            "repo_name": item["name"], "full_name": item["full_name"], "url": item["html_url"],
            "description": item.get("description") or "", "language": item.get("language") or "",
            "stars": item.get("stargazers_count", 0), "forks": item.get("forks_count", 0),
            "open_issues": item.get("open_issues_count", 0), "pushed_at": item.get("pushed_at"),
            "topics": item.get("topics", []),
        }

    @staticmethod
    def mock(limit: int = 10) -> list[dict]:
        now = datetime.now(timezone.utc).isoformat()
        return [{"repo_name": full.split("/")[-1], "full_name": full, "url": f"https://github.com/{full}",
                 "description": desc, "stars": stars, "forks": forks, "open_issues": 0,
                 "language": lang, "topics": topics, "pushed_at": now}
                for full, desc, stars, forks, lang, topics in MOCK_REPOS[:limit]]

