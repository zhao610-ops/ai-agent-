import json
import time
from datetime import datetime

from sqlalchemy.orm import Session

from app.agents.base_agent import BaseAgent
from app.config import get_settings
from app.database import PushLog
from app.services.settings_service import get_serverchan_config
from app.tools.serverchan_tool import ServerChanTool


class ServerChanPushAgent(BaseAgent):
    name = "ServerChanPushAgent"

    def run(self, session: Session, week: str, context: dict) -> dict:
        context.setdefault("agent_errors", {})
        config = get_serverchan_config(session, include_secret=True)
        title = f"AI Agent 周报｜{week}"
        top_words = "、".join(item["keyword"] for item in context["trends"][:5])
        repos = "\n".join(f'{i}. {row["full_name"]}：+{row["stars_growth_7d"]}' for i, row in enumerate(context["repos"][:3], 1))
        desp = f'## 本周核心判断\n\n{context["report"]["summary"]}\n\n## 本周热词\n\n{top_words}\n\n## GitHub 热门项目\n\n{repos}\n\n## 完整周报\n\n{get_settings().frontend_url}/reports/{week}'
        settings = get_settings()
        demo_skipped = not getattr(settings, "allow_real_push", True)
        # 安全开关优先级最高，即使数据库中保存了 SendKey 也不能绕过。
        if demo_skipped:
            status, response, error = "skipped", {"demo": True}, "演示模式下未真实请求外部服务，未真实推送微信"
        elif not context.get("allow_push", False):
            status, response, error = "skipped", {}, "等待用户确认推送"
        elif not config["enabled"] or not config["sendkey_configured"]:
            status, response, error = "skipped", {}, "Server 酱未启用或未配置 SendKey"
        else:
            response, error, status = {}, "", "failed"
            tool = ServerChanTool(config["api_base"], config["sendkey"])
            # 仅显式推送进入重试，最多三次，自动流水线不会触发网络请求。
            for retry_count in range(3):
                try:
                    response = tool.push(title, desp)
                    status, error = "success", ""
                    break
                except Exception as exc:
                    error = str(exc)
                    if retry_count < 2:
                        time.sleep(retry_count + 1)
        retry_count = retry_count if not demo_skipped and context.get("allow_push", False) and config["enabled"] and config["sendkey_configured"] else 0
        if error:
            context["agent_errors"].setdefault(self.name, []).append(error)
        log = PushLog(week=week, title=title, content=desp, status=status,
                      response=json.dumps(response, ensure_ascii=False), error_message=error,
                      retry_count=retry_count,
                      pushed_at=datetime.now() if status == "success" else None)
        session.add(log); session.commit()
        return {"status": status, "error": error, "log_id": log.id, "demo": demo_skipped, "_output_count": 1}
