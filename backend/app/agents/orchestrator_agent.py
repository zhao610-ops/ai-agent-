import json
from datetime import datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from app.agents.github_agent import GitHubAgent
from app.agents.news_agent import NewsAgent
from app.agents.report_agent import ReportAgent
from app.agents.serverchan_push_agent import ServerChanPushAgent
from app.agents.trend_agent import TrendAgent
from app.agents.visualization_agent import VisualizationAgent
from app.database import AgentRun, WeeklyReport


class OrchestratorAgent:
    name = "OrchestratorAgent"

    def run(self, session: Session, week: str | None = None) -> dict:
        week = week or datetime.now().strftime("%G-W%V")
        run_id = uuid4().hex
        orchestration_log = AgentRun(run_id=run_id, week=week, agent_name=self.name, status="running", input="{}")
        session.add(orchestration_log); session.commit()
        try:
            result = self._run_pipeline(session, run_id, week)
            orchestration_log.status = "success"
            orchestration_log.output = json.dumps(result, ensure_ascii=False)
            return result
        except Exception as exc:
            orchestration_log.status = "failed"
            orchestration_log.error = str(exc)
            raise
        finally:
            orchestration_log.finished_at = datetime.now()
            session.commit()

    def _run_pipeline(self, session: Session, run_id: str, week: str) -> dict:
        context = {"fallbacks": []}
        context["articles"] = NewsAgent().execute(session, run_id, week, context)
        context["repos"] = GitHubAgent().execute(session, run_id, week, context)
        context["trends"] = TrendAgent().execute(session, run_id, week, context)
        context["charts"] = VisualizationAgent().execute(session, run_id, week, context)
        context["report"] = ReportAgent().execute(session, run_id, week, context)
        report_data = context["report"]
        report = session.query(WeeklyReport).filter(WeeklyReport.week == week).first()
        values = {
            "title": f"AI Agent 周报｜{week}", "summary": report_data["summary"],
            "content_md": report_data["content_md"], "content_html": report_data["content_html"],
            **context["charts"], "report_path": report_data["report_path"],
            "llm_enabled": report_data["llm_enabled"], "llm_provider": report_data["llm_provider"],
            "llm_model": report_data["llm_model"], "generation_mode": report_data["generation_mode"],
        }
        if report:
            for key, value in values.items(): setattr(report, key, value)
        else:
            report = WeeklyReport(week=week, **values); session.add(report)
        session.commit()
        context["push"] = ServerChanPushAgent().execute(session, run_id, week, context)
        if context["push"]["status"] == "success":
            report.pushed_at = datetime.now(); session.commit()
        return {"run_id": run_id, "week": week, "report_id": report.id,
                "generation_mode": report.generation_mode, "fallbacks": context["fallbacks"],
                "push": context["push"]}
