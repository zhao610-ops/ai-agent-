from sqlalchemy.orm import Session

from app.database import PushLog


def latest_push_logs(session: Session, limit: int = 50) -> list[PushLog]:
    return session.query(PushLog).order_by(PushLog.created_at.desc()).limit(limit).all()
