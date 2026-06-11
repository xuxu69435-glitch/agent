import json
from typing import Any

from llm.base import BaseLLM, Message
from tools import execute_tool, get_tool_schemas
from tools.sandbox import get_workspace

SYSTEM_PROMPT = """你是一个智能编程助手 Agent，可以使用工具来完成任务。

可用能力：
- 读取、写入、搜索文件
- 查看项目结构
- 执行 shell 命令
- 生成并保存分析报告

工作流程：
1. 理解用户需求
2. 使用合适的工具收集信息
3. 分析并给出结论
4. 必要时将结果保存为报告

请用中文回复用户。"""


def _build_system_prompt() -> str:
    workspace = get_workspace()
    if workspace is None:
        return SYSTEM_PROMPT
    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"安全限制：所有文件操作和命令执行均限制在工作区 `{workspace}` 内，"
        f"不要尝试访问工作区外的路径。"
    )


class Agent:
    """Agent 核心类，负责协调 LLM 与工具调用。"""

    def __init__(self, llm: BaseLLM, max_iterations: int = 10):
        self.llm = llm
        self.max_iterations = max_iterations
        self.messages: list[Message] = [Message(role="system", content=_build_system_prompt())]

    def run(self, user_input: str) -> str:
        """处理用户输入，自动进行多轮工具调用，返回最终回复。"""
        self.messages.append(Message(role="user", content=user_input))

        for _ in range(self.max_iterations):
            response = self.llm.chat(self.messages, tools=get_tool_schemas())
            self.messages.append(response)

            if not response.tool_calls:
                return response.content

            for tool_call in response.tool_calls:
                result = execute_tool(tool_call["name"], tool_call["arguments"])
                self.messages.append(Message(
                    role="tool",
                    content=json.dumps({"result": result}, ensure_ascii=False),
                ))

        return "已达到最大迭代次数，请简化任务后重试。"

    def reset(self):
        """重置对话历史。"""
        self.messages = [Message(role="system", content=_build_system_prompt())]

    def get_history(self) -> list[dict[str, Any]]:
        """返回对话历史（用于调试）。"""
        return [{"role": m.role, "content": m.content} for m in self.messages]
