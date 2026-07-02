# AI Agent 微信周报助手

每周采集 AI Agent 新闻和 GitHub 热门项目，分析关键词趋势，生成中文周报与图表，并通过 Server 酱推送摘要。

## 功能

- 多 Agent 编排及完整运行日志
- RSS、GitHub API 采集，失败时自动使用 mock 数据
- 热词、增长趋势和三类图表
- 模板周报与 OpenAI 兼容大模型周报，模型失败自动降级
- SQLite 配置与历史数据存储
- Server 酱测试推送与自动推送
- FastAPI API、APScheduler 周任务、Next.js 管理页面

## 启动后端

建议使用 Python 3.11 或 3.12。

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m uvicorn app.main:app --reload --port 8000
```

接口文档：http://localhost:8000/docs

## 启动前端

```powershell
cd frontend
npm install
Copy-Item .env.local.example .env.local
npm run dev
```

页面：http://localhost:3000

## 配置

密钥只放在 `backend/.env` 或通过设置页保存到 SQLite，不要提交到版本库。

- `GITHUB_TOKEN`：可选，提高 GitHub API 限额。
- `SERVER_CHAN_SENDKEY`：Server 酱 SendKey。
- `LLM_ENABLED=false`：默认关闭大模型。
- `LLM_PROVIDER`、`LLM_API_KEY`、`LLM_BASE_URL`、`LLM_MODEL`：模型默认配置。

设置页保存的模型配置优先于 `.env`。API Key 永远不会通过查询接口明文返回。

## 定时任务

默认按 `Asia/Shanghai` 时区每周一 08:30 运行，可通过 `.env` 中的 `SCHEDULE_*` 修改。生产环境应只启动一个包含调度器的后端进程，避免重复执行任务。
