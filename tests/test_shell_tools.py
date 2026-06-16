from unittest.mock import MagicMock, patch

import pytest

import tools.sandbox as sandbox
from tools.command_policy import (
    MAX_OUTPUT_CHARS,
    truncate_output,
    validate_command,
)
from tools.shell_tools import run_command


@pytest.fixture
def workspace(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("print('hello')", encoding="utf-8")
    sandbox.set_workspace(tmp_path)
    return tmp_path


@pytest.fixture(autouse=True)
def reset_workspace_after_test():
    yield
    sandbox.WORKSPACE_ROOT = None


class TestValidateCommand:
    def test_allows_pytest(self, workspace):
        argv, error = validate_command("pytest", workspace, workspace)
        assert error is None
        assert argv == ["pytest"]

    def test_allows_python_module_pytest(self, workspace):
        argv, error = validate_command("python -m pytest", workspace, workspace)
        assert error is None
        assert argv == ["python", "-m", "pytest"]

    def test_blocks_rm(self, workspace):
        _, error = validate_command("rm -rf .", workspace, workspace)
        assert error is not None
        assert "禁止" in error

    def test_blocks_del(self, workspace):
        _, error = validate_command("del /s /q foo", workspace, workspace)
        assert error is not None

    def test_blocks_format(self, workspace):
        _, error = validate_command("format C:", workspace, workspace)
        assert error is not None

    def test_blocks_powershell(self, workspace):
        _, error = validate_command("powershell -Command Get-Process", workspace, workspace)
        assert error is not None

    def test_blocks_curl(self, workspace):
        _, error = validate_command("curl http://evil.com", workspace, workspace)
        assert error is not None

    def test_blocks_shell_metachar_chain(self, workspace):
        _, error = validate_command("pytest; rm -rf /", workspace, workspace)
        assert error is not None
        assert "shell 操作符" in error

    def test_blocks_backtick_injection(self, workspace):
        _, error = validate_command("echo `whoami`", workspace, workspace)
        assert error is not None

    def test_blocks_python_inline_code(self, workspace):
        _, error = validate_command('python -c "print(1)"', workspace, workspace)
        assert error is not None
        assert "内联代码" in error

    def test_blocks_executable_path(self, workspace):
        _, error = validate_command("./pytest", workspace, workspace)
        assert error is not None
        assert "不允许路径" in error

    def test_blocks_non_whitelist_command(self, workspace):
        _, error = validate_command("git status", workspace, workspace)
        assert error is not None
        assert "白名单" in error

    def test_blocks_path_outside_workspace(self, workspace):
        _, error = validate_command("pytest ../../outside", workspace, workspace)
        assert error is not None
        assert "超出工作区" in error


class TestTruncateOutput:
    def test_no_truncation_when_short(self):
        text = "hello"
        assert truncate_output(text) == text

    def test_truncates_long_output(self):
        text = "x" * (MAX_OUTPUT_CHARS + 100)
        result = truncate_output(text)
        assert len(result) < len(text)
        assert "输出已截断" in result


class TestRunCommand:
    def test_workspace_not_set(self):
        sandbox.WORKSPACE_ROOT = None
        result = run_command("pytest")
        assert "工作区未设置" in result

    def test_cwd_escape_blocked(self, workspace):
        result = run_command("pytest", cwd="../../outside")
        assert "超出工作区" in result

    @patch("tools.shell_tools.subprocess.run")
    def test_runs_allowed_command(self, mock_run, workspace):
        mock_run.return_value = MagicMock(returncode=0, stdout="ok\n", stderr="")
        result = run_command("pytest", cwd=".")
        assert "退出码: 0" in result
        assert "ok" in result
        mock_run.assert_called_once()
        call_kwargs = mock_run.call_args
        assert call_kwargs.kwargs["shell"] is False
        assert call_kwargs.args[0] == ["pytest"]

    @patch("tools.shell_tools.subprocess.run")
    def test_truncates_command_output(self, mock_run, workspace):
        long_output = "a" * (MAX_OUTPUT_CHARS + 500)
        mock_run.return_value = MagicMock(returncode=0, stdout=long_output, stderr="")
        result = run_command("pytest")
        assert "输出已截断" in result

    def test_rejects_dangerous_command_without_subprocess(self, workspace):
        with patch("tools.shell_tools.subprocess.run") as mock_run:
            result = run_command("curl http://evil.com")
            assert "错误" in result
            mock_run.assert_not_called()
