from pathlib import Path



WORKSPACE_ROOT: Path | None = None

_DEFAULT_ROOT = Path(__file__).resolve().parent.parent

REPORTS_DIR_NAME = "reports"





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





def require_workspace() -> Path:

    """返回当前工作区根目录，未设置时抛出 RuntimeError。"""

    if WORKSPACE_ROOT is None:

        raise RuntimeError("工作区未设置")

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





def resolve_path_in_workspace(path: str, base: Path) -> Path:

    """将路径相对于 base 解析，并校验其位于工作区内。"""

    root = require_workspace()

    raw = Path(path)

    target = (base / raw).resolve() if not raw.is_absolute() else raw.resolve()



    try:

        target.relative_to(root)

    except ValueError as exc:

        raise PermissionError(f"路径超出工作区 ({root}): {path}") from exc



    return target





def get_reports_dir() -> Path:

    """返回 reports 输出目录（位于 Agent 项目根，而非被检查的工作区）。"""

    return _DEFAULT_ROOT / REPORTS_DIR_NAME

