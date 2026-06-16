from agent.tool_router import execute_tool, get_tool_schemas


def test_all_tools_registered():
    schemas = get_tool_schemas()
    names = {s["function"]["name"] for s in schemas}
    assert names == {
        "list_files",
        "read_file",
        "search_code",
        "run_command",
        "git_status",
        "git_diff",
        "write_report",
    }


def test_unknown_tool():
    result = execute_tool("nonexistent", {})
    assert not result.success
    assert "未知工具" in result.output


def test_missing_required_param():
    result = execute_tool("read_file", {})
    assert not result.success
    assert "缺少必填参数" in result.output
