import subprocess

from .sandbox import resolve_safe


def _run_git(args: list[str], cwd: str) -> str:
    try:
        work_dir = resolve_safe(cwd)
    except PermissionError as e:
        return f"错误：{e}"
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=work_dir,
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = (result.stdout + result.stderr).strip() or "（无输出）"
        if result.returncode != 0:
            return f"git 命令失败 (退出码 {result.returncode}):\n{output}"
        return output
    except FileNotFoundError:
        return "错误：未找到 git 命令，请确认已安装 Git"
    except subprocess.TimeoutExpired:
        return "错误：git 命令执行超时"
    except Exception as e:
        return f"错误：{e}"


def git_status(cwd: str = ".") -> str:
    """查看 Git 工作区状态。"""
    return _run_git(["status", "--short", "--branch"], cwd)


def git_diff(cwd: str = ".", staged: bool = False) -> str:
    """查看 Git diff。"""
    args = ["diff"]
    if staged:
        args.append("--staged")
    return _run_git(args, cwd)


SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "git_status",
            "description": "查看 Git 仓库状态（分支与变更文件）",
            "parameters": {
                "type": "object",
                "properties": {
                    "cwd": {"type": "string", "description": "仓库目录，默认为工作区根"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "git_diff",
            "description": "查看 Git diff（工作区或暂存区变更）",
            "parameters": {
                "type": "object",
                "properties": {
                    "cwd": {"type": "string", "description": "仓库目录"},
                    "staged": {"type": "boolean", "description": "是否查看暂存区 diff"},
                },
                "required": [],
            },
        },
    },
]

HANDLERS = {
    "git_status": git_status,
    "git_diff": git_diff,
}
