import json
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.database import AgentRun


class BaseAgent:
    name = "BaseAgent"

    def execute(self, session: Session, run_id: str, week: str, context: dict) -> Any:
        log = AgentRun(run_id=run_id, week=week, agent_name=self.name, status="running",
                       input=json.dumps(self.summarize_input(context), ensure_ascii=False, default=str))
        session.add(log); session.commit()
        try:
            result = self.run(session, week, context)
            log.status = "success"
            log.output = json.dumps(self.summarize_output(result), ensure_ascii=False, default=str)
            return result
        except Exception as exc:
            log.status = "failed"
            log.error = str(exc)
            raise
        finally:
            log.finished_at = datetime.now()
            session.commit()

    def run(self, session: Session, week: str, context: dict) -> Any:
        raise NotImplementedError

    @staticmethod
    def summarize_input(context: dict) -> dict:
        return {key: len(value) if isinstance(value, list) else str(value)[:200] for key, value in context.items()}

    @staticmethod
    def summarize_output(result: Any) -> Any:
        return {"count": len(result)} if isinstance(result, list) else result

