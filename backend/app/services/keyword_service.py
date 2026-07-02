import re
from collections import Counter

import jieba
from sqlalchemy.orm import Session

from app.database import KeywordStat


STOPWORDS = {"这个", "一个", "进行", "使用", "通过", "相关", "项目", "系统", "能力", "开始", "成为", "正在", "可以", "智能", "人工智能"}
ALIASES = {"agent": "Agent", "agents": "Agent", "multi-agent": "Multi-Agent", "workflow": "Workflow", "mcp": "MCP", "rag": "RAG", "llm": "LLM"}


def extract_keywords(texts: list[str], top_n: int = 30) -> Counter:
    counter: Counter = Counter()
    for text in texts:
        normalized = re.sub(r"[^\w\-\u4e00-\u9fff]+", " ", text.lower())
        for token in jieba.cut(normalized):
            word = token.strip()
            if len(word) < 2 or word in STOPWORDS or word.isdigit():
                continue
            counter[ALIASES.get(word, word)] += 1
    return Counter(dict(counter.most_common(top_n)))


def save_keyword_stats(session: Session, week: str, frequencies: Counter, news_texts: list[str], repo_texts: list[str]) -> list[dict]:
    previous_rows = session.query(KeywordStat).filter(KeywordStat.week < week).order_by(KeywordStat.week.desc()).all()
    previous = {}
    for row in previous_rows:
        previous.setdefault(row.keyword, row.frequency)
    session.query(KeywordStat).filter(KeywordStat.week == week).delete()
    results = []
    for keyword, frequency in frequencies.items():
        news_count = sum(keyword.lower() in text.lower() for text in news_texts)
        github_count = sum(keyword.lower() in text.lower() for text in repo_texts)
        old = previous.get(keyword, 0)
        growth_rate = ((frequency - old) / old * 100) if old else (100.0 if frequency else 0)
        trend_score = round(frequency * 0.7 + max(growth_rate, 0) * 0.03, 2)
        row = KeywordStat(keyword=keyword, week=week, frequency=frequency,
                          source_count=news_count + github_count, github_count=github_count,
                          news_count=news_count, growth_rate=round(growth_rate, 2), trend_score=trend_score)
        session.add(row)
        results.append({"keyword": keyword, "frequency": frequency, "source_count": row.source_count,
                        "github_count": github_count, "news_count": news_count,
                        "growth_rate": row.growth_rate, "trend_score": trend_score})
    session.commit()
    return sorted(results, key=lambda item: item["trend_score"], reverse=True)

