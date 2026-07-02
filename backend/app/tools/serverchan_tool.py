import requests


class ServerChanTool:
    def __init__(self, api_base: str, sendkey: str, timeout: int = 20):
        self.api_base = api_base.rstrip("/")
        self.sendkey = sendkey
        self.timeout = timeout

    def push(self, title: str, desp: str) -> dict:
        if not self.sendkey:
            raise ValueError("未配置 Server 酱 SendKey")
        response = requests.post(
            f"{self.api_base}/{self.sendkey}.send",
            data={"title": title, "desp": desp},
            timeout=self.timeout,
        )
        response.raise_for_status()
        result = response.json()
        if result.get("code") not in (0, None):
            raise RuntimeError(result.get("message") or "Server 酱推送失败")
        return result

