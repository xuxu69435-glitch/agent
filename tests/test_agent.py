from agent.agent import Agent
from agent.types import Message, ToolResult


class FakeLLM:
    def __init__(self):
        self.calls = 0
        self.messages = []

    def chat(self, messages, tools=None):
        self.messages = list(messages)
        self.calls += 1
        if self.calls == 1:
            return Message(
                role="assistant",
                content="",
                tool_calls=[
                    {
                        "id": "call_123",
                        "name": "list_files",
                        "arguments": {"path": "."},
                    }
                ],
            )
        return Message(role="assistant", content="done")


def test_agent_preserves_tool_call_id(monkeypatch):
    llm = FakeLLM()
    agent = Agent(llm)
    monkeypatch.setattr(
        agent,
        "_dispatch_tool_call",
        lambda tool_call: ToolResult(
            tool_call_id=tool_call["id"],
            name=tool_call["name"],
            output="ok",
        ),
    )

    assert agent.run("inspect") == "done"
    tool_message = llm.messages[-1]
    assert tool_message.role == "tool"
    assert tool_message.tool_call_id == "call_123"
