import json
from typing import Any

from llm.base import BaseLLM
from tools.sandbox import get_workspace

from .prompts import build_system_prompt
from .tool_router import execute_tool, get_tool_schemas
from .types import Message, ToolResult


class Agent:
    """Agent 主循环：协调 LLM 与工具调用。"""

    def __init__(self, llm: BaseLLM, max_iterations: int = 10):
        self.llm = llm
        self.max_iterations = max_iterations
        self.messages: list[Message] = [
            Message(role="system", content=build_system_prompt(get_workspace()))
        ]

    def run(self, user_input: str) -> str:
        self.messages.append(Message(role="user", content=user_input))

        for _ in range(self.max_iterations):
            response = self.llm.chat(self.messages, tools=get_tool_schemas())
            self.messages.append(response)

            if not response.tool_calls:
                return response.content

            for tool_call in response.tool_calls:
                result = self._dispatch_tool_call(tool_call)
                self.messages.append(Message(
                    role="tool",
                    content=json.dumps(
                        {"result": result.output, "success": result.success},
                        ensure_ascii=False,
                    ),
                    tool_call_id=result.tool_call_id,
                ))

        return "已达到最大迭代次数，请简化任务后重试。"

    def _dispatch_tool_call(self, tool_call: dict[str, Any]) -> ToolResult:
        result = execute_tool(tool_call["name"], tool_call["arguments"])
        result.tool_call_id = tool_call.get("id", "")
        return result

    def reset(self) -> None:
        self.messages = [
            Message(role="system", content=build_system_prompt(get_workspace()))
        ]

    def get_history(self) -> list[dict[str, Any]]:
        return [{"role": m.role, "content": m.content} for m in self.messages]
