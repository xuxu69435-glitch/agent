import os
import re
import shlex
from pathlib import Path

from .sandbox import resolve_path_in_workspace

MAX_OUTPUT_CHARS = 32_768

ALLOWED_EXECUTABLES = {
    "python", "python3", "py", "pytest", "ruff", "mypy", "black", "flake8", "pylint",
    "node", "npm", "npx", "yarn", "pnpm",
    "cargo", "go", "make", "cmake", "dotnet", "mvn", "gradle",
    "java", "javac", "ruby", "bundle", "php", "composer",
}

INLINE_CODE_EXECUTABLES = {"python", "python3", "py", "node"}
INLINE_CODE_FLAGS = {"-c", "--eval", "-e"}

SHELL_METACHAR_PATTERN = re.compile(r"[;|&`><]|\$\(|\|\||&&")

DANGEROUS_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\brm\b", r"\brmdir\b", r"\bdel\b", r"\berase\b", r"\bformat\b",
        r"\bmkfs\b", r"\bdd\b",
        r"\bpowershell\b", r"\bpwsh\b", r"\bcmd\b", r"\bbash\b", r"\bsh\b", r"\bzsh\b",
        r"\bcurl\b", r"\bwget\b", r"\binvoke-webrequest\b", r"\biwr\b",
        r"\bshutdown\b", r"\breboot\b", r"\breg\b", r"\bnet\s+user\b", r"taskkill\s+/f",
    )
]


def truncate_output(text: str, limit: int = MAX_OUTPUT_CHARS) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n... (输出已截断，共 {len(text)} 字符)"


def _normalize_executable_name(name: str) -> str:
    lower = name.lower()
    for suffix in (".exe", ".cmd", ".bat", ".com"):
        if lower.endswith(suffix):
            return lower[: -len(suffix)]
    return lower


def _executable_has_path(argv0: str) -> bool:
    return "/" in argv0 or "\\" in argv0 or argv0.startswith(".")


def _looks_like_path(token: str) -> bool:
    if token.startswith("-"):
        return False
    if token.startswith("."):
        return True
    return "/" in token or "\\" in token


def _check_inline_code_flags(executable: str, argv: list[str]) -> str | None:
    if executable not in INLINE_CODE_EXECUTABLES:
        return None
    for arg in argv[1:]:
        if arg in INLINE_CODE_FLAGS:
            return f"禁止内联代码执行: {argv[0]} {arg}"
    return None


def validate_command(
    command: str,
    work_dir: Path,
    _workspace_root: Path,
) -> tuple[list[str] | None, str | None]:
    command = command.strip()
    if not command:
        return None, "命令不能为空"

    if SHELL_METACHAR_PATTERN.search(command):
        return None, "命令包含禁止的 shell 操作符 (; | & ` > < && || $())"

    for pattern in DANGEROUS_PATTERNS:
        if pattern.search(command):
            return None, f"命令包含禁止的模式: {pattern.pattern}"

    try:
        argv = shlex.split(command, posix=os.name != "nt")
    except ValueError as exc:
        return None, f"命令解析失败: {exc}"

    if not argv:
        return None, "命令不能为空"

    if _executable_has_path(argv[0]):
        return None, f"可执行文件必须是 PATH 中的命令名，不允许路径: {argv[0]}"

    executable = _normalize_executable_name(Path(argv[0]).name)
    if executable not in ALLOWED_EXECUTABLES:
        return None, f"命令不在白名单内: {argv[0]}"

    inline_error = _check_inline_code_flags(executable, argv)
    if inline_error:
        return None, inline_error

    for token in argv[1:]:
        if _looks_like_path(token):
            try:
                resolve_path_in_workspace(token, work_dir)
            except PermissionError as exc:
                return None, str(exc)

    return argv, None
