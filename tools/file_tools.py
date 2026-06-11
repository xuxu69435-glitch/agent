from pathlib import Path

from .sandbox import resolve_safe


def read_file(path: str) -> str:
    """读取文件内容。"""
    try:
        file_path = resolve_safe(path)
    except PermissionError as e:
        return f"错误：{e}"
    if not file_path.exists():
        return f"错误：文件不存在 - {path}"
    if not file_path.is_file():
        return f"错误：路径不是文件 - {path}"
    return file_path.read_text(encoding="utf-8")


def write_file(path: str, content: str) -> str:
    """写入文件内容。"""
    try:
        file_path = resolve_safe(path)
    except PermissionError as e:
        return f"错误：{e}"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
    return f"成功写入文件：{path}"


def list_directory(path: str = ".") -> str:
    """列出目录内容。"""
    try:
        dir_path = resolve_safe(path)
    except PermissionError as e:
        return f"错误：{e}"
    if not dir_path.exists():
        return f"错误：目录不存在 - {path}"
    if not dir_path.is_dir():
        return f"错误：路径不是目录 - {path}"

    entries = []
    for entry in sorted(dir_path.iterdir()):
        prefix = "[DIR] " if entry.is_dir() else "[FILE]"
        entries.append(f"{prefix} {entry.name}")

    return "\n".join(entries) if entries else "（空目录）"


def search_files(directory: str, pattern: str) -> str:
    """在目录中按文件名模式搜索文件。"""
    try:
        dir_path = resolve_safe(directory)
    except PermissionError as e:
        return f"错误：{e}"
    if not dir_path.exists():
        return f"错误：目录不存在 - {directory}"

    matches = sorted(str(p) for p in dir_path.rglob(pattern))
    return "\n".join(matches) if matches else f"未找到匹配 '{pattern}' 的文件"


FILE_TOOLS = {
    "read_file": {
        "function": read_file,
        "schema": {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "读取指定路径的文件内容",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "文件路径"},
                    },
                    "required": ["path"],
                },
            },
        },
    },
    "write_file": {
        "function": write_file,
        "schema": {
            "type": "function",
            "function": {
                "name": "write_file",
                "description": "将内容写入指定路径的文件",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "文件路径"},
                        "content": {"type": "string", "description": "要写入的内容"},
                    },
                    "required": ["path", "content"],
                },
            },
        },
    },
    "list_directory": {
        "function": list_directory,
        "schema": {
            "type": "function",
            "function": {
                "name": "list_directory",
                "description": "列出指定目录下的文件和子目录",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "目录路径，默认为当前目录"},
                    },
                    "required": [],
                },
            },
        },
    },
    "search_files": {
        "function": search_files,
        "schema": {
            "type": "function",
            "function": {
                "name": "search_files",
                "description": "在目录中按 glob 模式搜索文件",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "directory": {"type": "string", "description": "搜索目录"},
                        "pattern": {"type": "string", "description": "glob 匹配模式，如 *.py"},
                    },
                    "required": ["directory", "pattern"],
                },
            },
        },
    },
}
