import json
from typing import Any

from openai import OpenAI

from .base import BaseLLM, Message


class OpenAIModel(BaseLLM):
    """OpenAI API 模型实现。"""

    def __init__(self, model: str = "gpt-4o", api_key: str | None = None, base_url: str | None = None):
        super().__init__(model, api_key, base_url)
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def chat(
        self,
        messages: list[Message],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.7,
    ) -> Message:
        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
        }
        if tools:
            kwargs["tools"] = tools

        response = self.client.chat.completions.create(**kwargs)
        choice = response.choices[0].message

        tool_calls = []
        if choice.tool_calls:
            for tc in choice.tool_calls:
                tool_calls.append({
                    "id": tc.id,
                    "name": tc.function.name,
                    "arguments": json.loads(tc.function.arguments),
                })

        return Message(
            role=choice.role,
            content=choice.content or "",
            tool_calls=tool_calls,
        )

    def stream_chat(
        self,
        messages: list[Message],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.7,
    ):
        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
            "stream": True,
        }
        if tools:
            kwargs["tools"] = tools

        stream = self.client.chat.completions.create(**kwargs)
        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                yield delta.content
