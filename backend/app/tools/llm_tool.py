import requests


class LLMTool:
    def __init__(self, base_url: str, model: str, api_key: str, timeout: int = 60):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key
        self.timeout = timeout

    def chat(self, messages: list[dict], temperature: float = 0.3) -> str:
        if not self.base_url or not self.model or not self.api_key:
            raise ValueError("模型配置不完整")
        url = f"{self.base_url}/chat/completions"
        response = requests.post(
            url,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            json={"model": self.model, "messages": messages, "temperature": temperature},
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()

    def test(self) -> str:
        return self.chat([{"role": "user", "content": "请只回复：模型连接成功"}], temperature=0)

