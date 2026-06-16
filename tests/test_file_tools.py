from tools.file_tools import list_files, read_file, search_code
from tools.sandbox import set_workspace


def test_file_tools(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "app.py").write_text("def hello():\n    return 'world'\n", encoding="utf-8")
    set_workspace(tmp_path)

    listing = list_files("src")
    assert "app.py" in listing

    content = read_file("src/app.py")
    assert "def hello" in content

    hits = search_code("src", "hello")
    assert "app.py" in hits
