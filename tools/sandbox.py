from pathlib import Path

WORKSPACE_ROOT: Path | None = None


def set_workspace(root: str | Path) -> Path:
    """设置 Agent 工作区根目录，所有工具操作均限制在该目录内。"""
    global WORKSPACE_ROOT
    WORKSPACE_ROOT = Path(root).resolve()
    if not WORKSPACE_ROOT.is_dir():
        raise NotADirectoryError(f"工作区不是有效目录: {WORKSPACE_ROOT}")
    return WORKSPACE_ROOT


def get_workspace() -> Path | None:
    """返回当前工作区根目录，未设置时返回 None。"""
    return WORKSPACE_ROOT


def resolve_safe(path: str) -> Path:
    """将路径解析为绝对路径，并校验其位于工作区内。"""
    if WORKSPACE_ROOT is None:
        return Path(path).resolve()

    root = WORKSPACE_ROOT
    raw = Path(path)
    target = (root / raw).resolve() if not raw.is_absolute() else raw.resolve()

    try:
        target.relative_to(root)
    except ValueError as exc:
        raise PermissionError(f"路径超出工作区 ({root}): {path}") from exc

    return target


def safe_filename(name: str) -> str:
    """校验文件名不含路径分隔符，防止目录穿越。"""
    if not name or name in (".", ".."):
        raise PermissionError(f"非法文件名: {name}")
    if "/" in name or "\\" in name or ".." in name:
        raise PermissionError(f"文件名不能包含路径: {name}")
    return name
