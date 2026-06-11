import json
import subprocess
from datetime import datetime
from pathlib import Path

from .sandbox import get_workspace, resolve_safe, safe_filename

_DEFAULT_ROOT = Path(__file__).resolve().parent.parent


def _reports_dir() -> Path:
    root = get_workspace() or _DEFAULT_ROOT
    return root / "reports"


def get_project_structure(root: str = ".", max_depth: int = 3) -> str:
    """获取项目目录树结构。"""
    try:
        root_path = resolve_safe(root)
    except PermissionError as e:
        return f"错误：{e}"
    if not root_path.exists():
        return f"错误：路径不存在 - {root}"

    lines: list[str] = []

    def _walk(path: Path, prefix: str = "", depth: int = 0):
        if depth > max_depth:
            return
        entries = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name))
        for i, entry in enumerate(entries):
            if entry.name.startswith(".") or entry.name == "__pycache__":
                continue
            is_last = i == len(entries) - 1
            connector = "└── " if is_last else "├── "
            lines.append(f"{prefix}{connector}{entry.name}")
            if entry.is_dir():
                extension = "    " if is_last else "│   "
                _walk(entry, prefix + extension, depth + 1)

    lines.append(root_path.name + "/")
    _walk(root_path)
    return "\n".join(lines)


def run_command(command: str, cwd: str = ".") -> str:
    """在项目目录中执行 shell 命令。"""
    try:
        work_dir = resolve_safe(cwd)
    except PermissionError as e:
        return f"错误：{e}"
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=work_dir,
            capture_output=True,
            text=True,
            timeout=60,
        )
        output = result.stdout or result.stderr or "（无输出）"
        return f"退出码: {result.returncode}\n{output}"
    except subprocess.TimeoutExpired:
        return "错误：命令执行超时（60秒）"
    except Exception as e:
        return f"错误：{e}"


def save_report(title: str, content: str) -> str:
    """将报告保存到 reports 目录。"""
    reports_dir = _reports_dir()
    reports_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_title = "".join(c if c.isalnum() or c in "-_" else "_" for c in title)
    filename = f"{timestamp}_{safe_title}.md"
    filepath = reports_dir / filename

    report = f"# {title}\n\n生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n---\n\n{content}"
    filepath.write_text(report, encoding="utf-8")
    return f"报告已保存：{filepath}"


def read_report(filename: str) -> str:
    """读取 reports 目录中的报告。"""
    try:
        safe_filename(filename)
        reports_dir = _reports_dir()
        filepath = reports_dir / filename
    except PermissionError as e:
        return f"错误：{e}"
    if not filepath.exists():
        available = [f.name for f in reports_dir.glob("*.md")] if reports_dir.exists() else []
        return f"错误：报告不存在 - {filename}\n可用报告：{', '.join(available) or '无'}"
    return filepath.read_text(encoding="utf-8")


def list_reports() -> str:
    """列出所有已保存的报告。"""
    reports_dir = _reports_dir()
    if not reports_dir.exists():
        return "暂无报告"
    reports = sorted(reports_dir.glob("*.md"), reverse=True)
    if not reports:
        return "暂无报告"
    return "\n".join(f.name for f in reports)


PROJECT_TOOLS = {
    "get_project_structure": {
        "function": get_project_structure,
        "schema": {
            "type": "function",
            "function": {
                "name": "get_project_structure",
                "description": "获取项目的目录树结构",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "root": {"type": "string", "description": "项目根目录路径"},
                        "max_depth": {"type": "integer", "description": "最大递归深度"},
                    },
                    "required": [],
                },
            },
        },
    },
    "run_command": {
        "function": run_command,
        "schema": {
            "type": "function",
            "function": {
                "name": "run_command",
                "description": "在项目目录中执行 shell 命令",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "要执行的命令"},
                        "cwd": {"type": "string", "description": "工作目录"},
                    },
                    "required": ["command"],
                },
            },
        },
    },
    "save_report": {
        "function": save_report,
        "schema": {
            "type": "function",
            "function": {
                "name": "save_report",
                "description": "将分析结果保存为 Markdown 报告",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "报告标题"},
                        "content": {"type": "string", "description": "报告正文内容"},
                    },
                    "required": ["title", "content"],
                },
            },
        },
    },
    "list_reports": {
        "function": list_reports,
        "schema": {
            "type": "function",
            "function": {
                "name": "list_reports",
                "description": "列出所有已保存的报告",
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
        },
    },
}
