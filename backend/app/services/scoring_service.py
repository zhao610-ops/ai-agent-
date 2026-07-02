def calculate_heat_score(relevance: float, popularity: float, freshness: float) -> float:
    """统一热度分，权重后续可通过历史效果继续校准。"""
    return round(relevance * 0.45 + popularity * 0.35 + freshness * 0.20, 2)

