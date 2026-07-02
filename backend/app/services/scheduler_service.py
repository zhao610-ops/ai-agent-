from apscheduler.schedulers.background import BackgroundScheduler

from app.agents.orchestrator_agent import OrchestratorAgent
from app.config import get_settings
from app.database import SessionLocal


scheduler = BackgroundScheduler(timezone=get_settings().timezone)


def scheduled_weekly_report() -> None:
    session = SessionLocal()
    try:
        OrchestratorAgent().run(session)
    finally:
        session.close()


def start_scheduler() -> None:
    settings = get_settings()
    if not scheduler.get_job("weekly-report"):
        scheduler.add_job(scheduled_weekly_report, "cron", id="weekly-report", day_of_week=settings.schedule_day,
                          hour=settings.schedule_hour, minute=settings.schedule_minute, replace_existing=True,
                          max_instances=1, coalesce=True)
    if not scheduler.running: scheduler.start()


def stop_scheduler() -> None:
    if scheduler.running: scheduler.shutdown(wait=False)

