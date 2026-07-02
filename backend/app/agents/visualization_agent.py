from pathlib import Path

from sqlalchemy.orm import Session

from app.agents.base_agent import BaseAgent
from app.config import get_settings
from app.tools.chart_tool import ChartTool


class VisualizationAgent(BaseAgent):
    name = "VisualizationAgent"

    def run(self, session: Session, week: str, context: dict) -> dict:
        output_dir = Path(get_settings().reports_dir) / week
        tool = ChartTool(output_dir)
        frequencies = {item["keyword"]: item["frequency"] for item in context["trends"]}
        return {
            "wordcloud_image": tool.wordcloud(frequencies),
            "github_chart_image": tool.github_growth(context["repos"]),
            "keyword_trend_image": tool.keyword_trend(context["trends"]),
        }

