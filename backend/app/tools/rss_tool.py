from datetime import datetime, timezone

import feedparser
import requests


MOCK_ARTICLES = [
    {"title": "MCP 推动 AI Agent 工具生态标准化", "url": "https://example.com/mcp-agent", "source": "Mock AI News", "summary": "模型上下文协议正在成为 Agent 连接外部工具的重要标准。"},
    {"title": "Browser Agent 从演示走向工作流自动化", "url": "https://example.com/browser-agent", "source": "Mock Tech", "summary": "浏览器智能体开始覆盖研究、测试和运营等真实流程。"},
    {"title": "Coding Agent 强化软件工程任务执行能力", "url": "https://example.com/coding-agent", "source": "Mock Developer", "summary": "编码智能体逐渐具备规划、工具调用、测试和迭代能力。"},
    {"title": "多 Agent 协作框架关注可观测性与可靠性", "url": "https://example.com/multi-agent", "source": "Mock Community", "summary": "Agent 编排、记忆、运行日志和故障恢复成为重点。"},
    {"title": "Agentic RAG 融合检索、推理和行动", "url": "https://example.com/agentic-rag", "source": "Mock Research", "summary": "RAG 系统正加入自主查询规划和工具执行能力。"},
]


class RSSTool:
    def __init__(self, timeout: int = 20):
        self.timeout = timeout

    def fetch(self, urls: list[str], limit: int = 20) -> list[dict]:
        items = []
        for url in urls:
            response = requests.get(url, timeout=self.timeout, headers={"User-Agent": "weekly-agent/1.0"})
            response.raise_for_status()
            feed = feedparser.parse(response.content)
            for entry in feed.entries:
                parsed = entry.get("published_parsed") or entry.get("updated_parsed")
                published = datetime(*parsed[:6], tzinfo=timezone.utc).isoformat() if parsed else None
                items.append({"title": entry.get("title", ""), "url": entry.get("link", ""),
                              "source": feed.feed.get("title", "RSS"), "published_at": published,
                              "summary": entry.get("summary", "")})
                if len(items) >= limit:
                    return items
        return items

    @staticmethod
    def mock() -> list[dict]:
        now = datetime.now(timezone.utc).isoformat()
        return [{**item, "published_at": now} for item in MOCK_ARTICLES]

