from .file_tools import FILE_TOOLS
from .project_tools import PROJECT_TOOLS
from .sandbox import get_workspace, set_workspace

ALL_TOOLS = {**FILE_TOOLS, **PROJECT_TOOLS}


def get_tool_schemas() -> list[dict]:
    """返回所有工具的 JSON Schema 列表，供 LLM 调用。"""
    return [tool["schema"] for tool in ALL_TOOLS.values()]


def execute_tool(name: str, arguments: dict) -> str:
    """根据工具名称和参数执行对应工具。"""
    if name not in ALL_TOOLS:
        return f"错误：未知工具 - {name}"
    try:
        result = ALL_TOOLS[name]["function"](**arguments)
        return str(result)
    except Exception as e:
        return f"工具执行错误 ({name}): {e}"
