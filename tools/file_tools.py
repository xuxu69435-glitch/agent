import re
from pathlib import Path

from .sandbox import resolve_safe

TEXT_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go", ".rs",
    ".c", ".cpp", ".h", ".hpp", ".cs", ".rb", ".php", ".swift",
    ".kt", ".scala", ".md", ".txt", ".json", ".yaml", ".yml",
    ".toml", ".xml", ".html", ".css", ".scss", ".sql", ".sh",
}


def list_files(path: str = ".") -> str:
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


def search_code(directory: str, pattern: str, file_glob: str = "*") -> str:
    """在源代码文件中搜索文本或正则模式。"""
    try:
        dir_path = resolve_safe(directory)
    except PermissionError as e:
        return f"错误：{e}"
    if not dir_path.exists():
        return f"错误：目录不存在 - {directory}"

    try:
        regex = re.compile(pattern)
    except re.error as e:
        return f"错误：无效正则表达式 - {e}"

    matches: list[str] = []
    for file_path in sorted(dir_path.rglob(file_glob)):
        if not file_path.is_file():
            continue
        if file_path.suffix and file_path.suffix not in TEXT_EXTENSIONS:
            continue
        try:
            lines = file_path.read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError, OSError):
            continue
        for lineno, line in enumerate(lines, start=1):
            if regex.search(line):
                rel = file_path.relative_to(dir_path)
                matches.append(f"{rel}:{lineno}: {line.strip()}")

    if not matches:
        return f"未找到匹配 '{pattern}' 的内容"
    if len(matches) > 100:
        return "\n".join(matches[:100]) + f"\n... 还有 {len(matches) - 100} 条结果"
    return "\n".join(matches)


SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
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
    {
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
    {
        "type": "function",
        "function": {
            "name": "search_code",
            "description": "在目录下的源代码文件中搜索文本或正则模式",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {"type": "string", "description": "搜索目录"},
                    "pattern": {"type": "string", "description": "搜索模式（支持正则）"},
                    "file_glob": {"type": "string", "description": "文件 glob 过滤，如 *.py"},
                },
                "required": ["directory", "pattern"],
            },
        },
    },
]

HANDLERS = {
    "list_files": list_files,
    "read_file": read_file,
    "search_code": search_code,
}
