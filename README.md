# Repo Inspector Agent

基于 LLM 的代码仓库检查 Agent，可浏览源码、搜索代码、查看 Git 变更并生成分析报告。

## 项目结构

```
repo-inspector-agent/
├── agent/
│   ├── agent.py              # Agent 主循环
│   ├── prompts.py            # 系统提示词、工具选择提示词
│   ├── tool_router.py        # 工具注册、参数校验、调用
│   └── types.py              # Message、ToolCall、ToolResult 等类型
├── llm/
│   ├── base.py               # BaseLLM 抽象类
│   ├── openai_model.py       # OpenAI 适配器
│   ├── deepseek_model.py     # DeepSeek 适配器
│   └── ollama_model.py       # Ollama 本地模型适配器
├── tools/
│   ├── file_tools.py         # list_files / read_file / search_code
│   ├── shell_tools.py        # run_command
│   ├── git_tools.py          # git_diff / git_status
│   └── report_tools.py       # write_report
├── examples/
│   └── sample_project/       # 示例待检查项目
├── reports/                  # Agent 输出的分析报告
├── tests/
├── main.py                   # CLI 入口
├── .env.example
└── pyproject.toml
```

## 快速开始

```powershell
# 1. 创建并激活本地虚拟环境
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. 安装依赖
pip install -e ".[dev]"

# 3. 配置 API Key
copy .env.example .env
# 编辑 .env 填入 DEEPSEEK_API_KEY 或 OPENAI_API_KEY

# 4. 启动（默认检查 examples/sample_project）
python main.py

# 检查指定仓库
python main.py -w D:\path\to\your\repo

# 单次执行
python main.py -p "列出项目结构并总结主要模块"
```

也可使用 `.\setup.ps1` 初始化环境，或 `.\run.ps1` 自动使用本地 `.venv` 启动。

## 工具一览

| 工具 | 说明 |
|------|------|
| `list_files` | 列出目录内容 |
| `read_file` | 读取文件 |
| `search_code` | 在源码中搜索关键字 |
| `git_status` | 查看 Git 状态 |
| `git_diff` | 查看 Git diff |
| `run_command` | 在工作区内执行命令 |
| `write_report` | 保存 Markdown 报告到 `reports/` |

## 运行测试

```powershell
pytest
```
