import requests


class WebSearchTool:
    """预留的通用公开搜索接口，业务 Agent 不绑定具体搜索厂商。"""

    def __init__(self, endpoint: str = "", api_key: str = "", timeout: int = 20):
        self.endpoint = endpoint
        self.api_key = api_key
        self.timeout = timeout

    def search(self, query: str) -> list[dict]:
        if not self.endpoint:
            raise ValueError("未配置网页搜索接口")
        response = requests.get(self.endpoint, params={"q": query}, headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return data.get("results", data.get("items", []))

