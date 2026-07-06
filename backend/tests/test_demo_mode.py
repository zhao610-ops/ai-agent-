from types import SimpleNamespace

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.agents.github_agent as github_agent_module
import app.agents.news_agent as news_agent_module
import app.agents.report_agent as report_agent_module
import app.agents.serverchan_push_agent as push_agent_module
import app.agents.visualization_agent as visualization_agent_module
import app.api.setting_routes as setting_routes_module
from app.agents.orchestrator_agent import OrchestratorAgent
from app.database import Base, PushLog, WeeklyReport
from app.tools.github_tool import GithubTool
from app.tools.llm_tool import LLMTool
from app.tools.rss_tool import RSSTool
from app.tools.serverchan_tool import ServerChanTool


def _forbid_external(*args, **kwargs):
    raise AssertionError("演示模式不允许请求外部服务")


def test_demo_pipeline_never_calls_external_services(tmp_path, monkeypatch):
    # 即使模拟已配置全部密钥，安全开关关闭时仍必须只走 mock 和模板路径。
    engine = create_engine(f"sqlite:///{tmp_path / 'demo.db'}")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, expire_on_commit=False)()
    settings = SimpleNamespace(
        demo_mode=True, public_demo=True, allow_real_push=False, allow_real_llm=False,
        github_token="should-not-be-used", news_rss_urls="https://invalid.example/rss",
        reports_dir=str(tmp_path / "reports"), frontend_url="http://localhost:3000",
    )
    for module in (news_agent_module, github_agent_module, report_agent_module, push_agent_module, visualization_agent_module):
        monkeypatch.setattr(module, "get_settings", lambda: settings)
    monkeypatch.setattr(RSSTool, "fetch", _forbid_external)
    monkeypatch.setattr(GithubTool, "search", _forbid_external)
    monkeypatch.setattr(LLMTool, "chat", _forbid_external)
    monkeypatch.setattr(ServerChanTool, "push", _forbid_external)
    monkeypatch.setattr(report_agent_module, "get_llm_config", lambda *args, **kwargs: {
        "enabled": True, "api_key_configured": True, "api_key": "configured-but-blocked",
        "provider": "custom", "base_url": "https://invalid.example", "model": "demo-model",
    })
    monkeypatch.setattr(push_agent_module, "get_serverchan_config", lambda *args, **kwargs: {
        "enabled": True, "sendkey_configured": True, "sendkey": "configured-but-blocked",
        "api_base": "https://invalid.example",
    })

    result = OrchestratorAgent().run(session, "2026-W29")
    report = session.query(WeeklyReport).filter_by(week="2026-W29").one()

    assert result["push"]["status"] == "skipped"
    assert result["push"]["demo"] is True
    assert report.generation_mode == "template"
    assert report.push_status == "not_pushed"
    for filename in ("report.md", "wordcloud.png", "github_growth_top10.png", "keyword_trend.png"):
        assert (tmp_path / "reports" / "2026-W29" / filename).exists()


def test_demo_test_buttons_return_success_without_external_requests(monkeypatch):
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    demo = SimpleNamespace(demo_mode=True, public_demo=True, allow_real_push=False, allow_real_llm=False)
    monkeypatch.setattr(setting_routes_module, "get_settings", lambda: demo)
    monkeypatch.setattr(LLMTool, "test", _forbid_external)
    monkeypatch.setattr(ServerChanTool, "push", _forbid_external)

    llm_result = setting_routes_module.test_llm(session)
    push_result = setting_routes_module.test_push(session)

    assert llm_result["success"] is True and llm_result["demo"] is True
    assert push_result["success"] is True and push_result["demo"] is True
    assert "未真实请求外部服务" in llm_result["output"]
    assert "未真实请求外部服务" in push_result["message"]
    assert session.query(PushLog).filter_by(status="skipped").count() == 1


def test_local_mode_keeps_real_test_paths(monkeypatch):
    # 本地显式允许真实能力时，原有工具调用路径保持可用。
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    local = SimpleNamespace(demo_mode=False, public_demo=False, allow_real_push=True, allow_real_llm=True)
    monkeypatch.setattr(setting_routes_module, "get_settings", lambda: local)
    monkeypatch.setattr(setting_routes_module, "get_llm_config", lambda *args, **kwargs: {
        "api_key_configured": True, "base_url": "https://example.com", "model": "test", "api_key": "test",
    })
    monkeypatch.setattr(setting_routes_module, "get_serverchan_config", lambda *args, **kwargs: {
        "enabled": True, "sendkey_configured": True, "api_base": "https://example.com", "sendkey": "test",
    })
    monkeypatch.setattr(LLMTool, "test", lambda self: "模型连接成功")
    monkeypatch.setattr(ServerChanTool, "push", lambda self, title, content: {"code": 0})

    assert setting_routes_module.test_llm(session)["output"] == "模型连接成功"
    assert setting_routes_module.test_push(session)["success"] is True
