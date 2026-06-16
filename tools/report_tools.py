from datetime import datetime

from .sandbox import get_reports_dir


def write_report(title: str, content: str) -> str:
    """将分析报告写入 reports 目录。"""
    reports_dir = get_reports_dir()
    reports_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_title = "".join(c if c.isalnum() or c in "-_" else "_" for c in title)
    filename = f"{timestamp}_{safe_title}.md"
    filepath = reports_dir / filename

    report = (
        f"# {title}\n\n"
        f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"---\n\n{content}"
    )
    filepath.write_text(report, encoding="utf-8")
    return f"报告已保存：{filepath}"


SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "write_report",
            "description": "将分析结果保存为 Markdown 报告到 reports/ 目录",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "报告标题"},
                    "content": {"type": "string", "description": "报告正文（Markdown）"},
                },
                "required": ["title", "content"],
            },
        },
    },
]

HANDLERS = {
    "write_report": write_report,
}
