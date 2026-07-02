from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.agent_routes import router as agent_router
from app.api.report_routes import router as report_router
from app.api.setting_routes import router as setting_router
from app.config import get_settings
from app.database import init_db
from app.services.scheduler_service import scheduler, start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db(); start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(title=get_settings().app_name, version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=[get_settings().frontend_url], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])
app.include_router(agent_router); app.include_router(report_router); app.include_router(setting_router)


@app.get("/health")
def health():
    return {"status": "ok", "scheduler_running": scheduler.running}
