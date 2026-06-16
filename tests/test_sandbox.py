import pytest

from tools.sandbox import resolve_safe, set_workspace


@pytest.fixture
def workspace(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("print('hello')", encoding="utf-8")
    set_workspace(tmp_path)
    return tmp_path


def test_resolve_safe_relative(workspace):
    path = resolve_safe("src/app.py")
    assert path.name == "app.py"


def test_resolve_safe_blocks_escape(workspace):
    with pytest.raises(PermissionError):
        resolve_safe("../../etc/passwd")
