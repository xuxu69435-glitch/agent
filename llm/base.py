from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Message:
    role: str
    content: str
    tool_calls: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]


class BaseLLM(ABC):
    """LLM 抽象基类，所有模型实现需继承此类。"""

    def __init__(self, model: str, api_key: str | None = None, base_url: str | None = None):
        self.model = model
        self.api_key = api_key
        self.base_url = base_url

    @abstractmethod
    def chat(
        self,
        messages: list[Message],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.7,
    ) -> Message:
        """发送对话请求并返回模型回复。"""
        ...

    @abstractmethod
    def stream_chat(
        self,
        messages: list[Message],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.7,
    ):
        """流式对话，逐块返回内容。"""
        ...
