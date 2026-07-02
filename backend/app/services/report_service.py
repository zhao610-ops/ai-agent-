import html
from pathlib import Path

import markdown


def build_template_report(week: str, articles: list[dict], repos: list[dict], trends: list[dict]) -> tuple[str, str]:
    hotwords = "、".join(item["keyword"] for item in trends[:10]) or "暂无"
    top_repo = repos[0]["full_name"] if repos else "暂无"
    summary = f"本周 AI Agent 领域重点关注 {hotwords}。GitHub 热门项目以 {top_repo} 为代表，工具调用、工作流和多 Agent 协作持续发展。"
    news_md = "\n".join(f'{i}. [{html.escape(row["title"])}]({row["url"]})：{row["summary"][:160]}' for i, row in enumerate(articles[:10], 1)) or "暂无新闻数据"
    repos_md = "\n".join(f'{i}. [{row["full_name"]}]({row["url"]})：{row["description"]}（Star {row["stars"]:,}，本周增长 +{row["stars_growth_7d"]}）' for i, row in enumerate(repos[:10], 1)) or "暂无项目数据"
    trend_md = "\n".join(f'- {row["keyword"]}：频次 {row["frequency"]}，趋势分 {row["trend_score"]}' for row in trends[:10])
    content = f"""# AI Agent 周报｜{week}

## 本周核心结论

{summary}

## 本周重要新闻

{news_md}

## GitHub 热门项目 TOP10

{repos_md}

## 本周热词

{hotwords}

## 趋势判断

{trend_md}

## 对 AI Agent 项目的启发

1. 将任务编排、工具调用日志和失败恢复作为基础能力。
2. 优先采用标准化工具协议，降低模型和工具之间的耦合。
3. 用持续快照衡量项目增长，不只看累计 Star。

## 原文链接

以上新闻与项目名称均已附原始链接。
"""
    return summary, content


def save_report_file(report_dir: Path, content: str) -> str:
    report_dir.mkdir(parents=True, exist_ok=True)
    path = report_dir / "report.md"
    path.write_text(content, encoding="utf-8")
    return str(path)


def to_html(content: str) -> str:
    return markdown.markdown(content, extensions=["tables", "fenced_code"])

