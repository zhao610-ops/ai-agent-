from sqlalchemy.orm import Session

from app.services.keyword_service import extract_keywords, save_keyword_stats
from app.agents.base_agent import BaseAgent


class TrendAgent(BaseAgent):
    name = "TrendAgent"

    def run(self, session: Session, week: str, context: dict) -> list[dict]:
        news_texts = [f'{row["title"]} {row["summary"]}' for row in context["articles"]]
        repo_texts = [f'{row["full_name"]} {row["description"]} {" ".join(row["topics"])}' for row in context["repos"]]
        return save_keyword_stats(session, week, extract_keywords(news_texts + repo_texts), news_texts, repo_texts)
