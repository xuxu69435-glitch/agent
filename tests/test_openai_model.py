import json

from agent.types import Message
from llm.openai_model import _serialize_message


def test_serializes_assistant_tool_call():
    message = Message(
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

    serialized = _serialize_message(message)

    assert serialized["tool_calls"] == [
        {
            "id": "call_123",
            "type": "function",
            "function": {
                "name": "list_files",
                "arguments": json.dumps({"path": "."}, ensure_ascii=False),
            },
        }
    ]


def test_serializes_tool_call_id():
    message = Message(
        role="tool",
        content='{"result": "ok", "success": true}',
        tool_call_id="call_123",
    )

    serialized = _serialize_message(message)

    assert serialized["tool_call_id"] == "call_123"
