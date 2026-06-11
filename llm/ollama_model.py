import json
from typing import Any

import requests

from .base import BaseLLM, Message


class OllamaModel(BaseLLM):
    """Ollama 本地模型实现。"""

    DEFAULT_BASE_URL = "http://localhost:11434"

    def __init__(self, model: str = "llama3", api_key: str | None = None, base_url: str | None = None):
        super().__init__(model, api_key, base_url or self.DEFAULT_BASE_URL)

    def chat(
        self,
        messages: list[Message],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.7,
    ) -> Message:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": False,
            "options": {"temperature": temperature},
        }
        if tools:
            payload["tools"] = tools

        response = requests.post(f"{self.base_url}/api/chat", json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()

        tool_calls = []
        if "tool_calls" in data.get("message", {}):
            for tc in data["message"]["tool_calls"]:
                tool_calls.append({
                    "id": tc.get("id", ""),
                    "name": tc["function"]["name"],
                    "arguments": tc["function"].get("arguments", {}),
                })

        return Message(
            role=data["message"]["role"],
            content=data["message"].get("content", ""),
            tool_calls=tool_calls,
        )

    def stream_chat(
        self,
        messages: list[Message],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.7,
    ):
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": True,
            "options": {"temperature": temperature},
        }
        if tools:
            payload["tools"] = tools

        with requests.post(f"{self.base_url}/api/chat", json=payload, stream=True, timeout=120) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if not line:
                    continue
                data = json.loads(line)
                content = data.get("message", {}).get("content", "")
                if content:
                    yield content
