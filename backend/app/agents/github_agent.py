import json
from datetime import datetime

from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import GithubRepo
from app.tools.github_tool import GithubTool
from app.agents.base_agent import BaseAgent


class GitHubAgent(BaseAgent):
    name = "GitHubAgent"

    def run(self, session: Session, week: str, context: dict) -> list[dict]:
        tool = GithubTool(get_settings().github_token)
        try:
            items = tool.search()
            if not items:
                raise RuntimeError("GitHub 未返回数据")
        except Exception:
            items = tool.mock()
            context["fallbacks"].append("GitHubAgent 使用 mock 数据")
        session.query(GithubRepo).filter(GithubRepo.week == week).delete()
        result = []
        for item in items:
            previous = session.query(GithubRepo).filter(GithubRepo.full_name == item["full_name"], GithubRepo.week < week).order_by(GithubRepo.week.desc()).first()
            growth = max(item["stars"] - previous.stars, 0) if previous else max(round(item["stars"] * 0.015), 1)
            pushed = datetime.fromisoformat(item["pushed_at"].replace("Z", "+00:00")).replace(tzinfo=None) if item.get("pushed_at") else None
            row = GithubRepo(week=week, **{key: item[key] for key in ("repo_name", "full_name", "url", "description", "language", "stars", "forks", "open_issues")},
                             pushed_at=pushed, stars_growth_7d=growth, topics=json.dumps(item["topics"], ensure_ascii=False),
                             agent_relevance_score=90, heat_score=round(growth * 0.3 + item["stars"] * 0.01, 2))
            session.add(row)
            result.append({**item, "stars_growth_7d": growth})
        session.commit()
        return sorted(result, key=lambda item: item["stars_growth_7d"], reverse=True)
