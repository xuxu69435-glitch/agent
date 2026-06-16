from typing import Any, Callable

from tools import file_tools, git_tools, report_tools, shell_tools

from .types import ToolResult

ToolHandler = Callable[..., str]

_REGISTRY: dict[str, dict[str, Any]] = {}


def _register(schemas: list[dict], handlers: dict[str, ToolHandler]) -> None:
    for schema in schemas:
        name = schema["function"]["name"]
        if name in _REGISTRY:
            raise ValueError(f"重复注册工具: {name}")
        _REGISTRY[name] = {
            "schema": schema,
            "handler": handlers[name],
            "required": schema["function"]["parameters"].get("required", []),
            "properties": schema["function"]["parameters"].get("properties", {}),
        }


def _validate_arguments(name: str, arguments: dict[str, Any]) -> str | None:
    entry = _REGISTRY[name]
    for key in entry["required"]:
        if key not in arguments:
            return f"缺少必填参数: {key}"
    for key in arguments:
        if key not in entry["properties"]:
            return f"未知参数: {key}"
    return None


def get_tool_schemas() -> list[dict]:
    return [entry["schema"] for entry in _REGISTRY.values()]


def execute_tool(name: str, arguments: dict[str, Any]) -> ToolResult:
    if name not in _REGISTRY:
        return ToolResult(tool_call_id="", name=name, output=f"错误：未知工具 - {name}", success=False)

    error = _validate_arguments(name, arguments)
    if error:
        return ToolResult(tool_call_id="", name=name, output=error, success=False)

    try:
        output = str(_REGISTRY[name]["handler"](**arguments))
        return ToolResult(tool_call_id="", name=name, output=output, success=True)
    except TypeError as e:
        return ToolResult(tool_call_id="", name=name, output=f"参数错误 ({name}): {e}", success=False)
    except Exception as e:
        return ToolResult(tool_call_id="", name=name, output=f"工具执行错误 ({name}): {e}", success=False)


def register_all_tools() -> None:
    _REGISTRY.clear()
    _register(file_tools.SCHEMAS, file_tools.HANDLERS)
    _register(shell_tools.SCHEMAS, shell_tools.HANDLERS)
    _register(git_tools.SCHEMAS, git_tools.HANDLERS)
    _register(report_tools.SCHEMAS, report_tools.HANDLERS)


register_all_tools()
