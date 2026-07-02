def deduplicate_by_url(items: list[dict]) -> list[dict]:
    seen: set[str] = set()
    result = []
    for item in items:
        url = item.get("url", "").strip()
        if url and url not in seen:
            seen.add(url)
            result.append(item)
    return result

