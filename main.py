import argparse
import os
import sys
from pathlib import Path

from agent import Agent
from llm import DeepSeekModel, OllamaModel, OpenAIModel
from tools import set_workspace

PROJECT_ROOT = Path(__file__).resolve().parent


def create_llm(provider: str, model: str, api_key: str | None, base_url: str | None):
    """根据 provider 创建对应的 LLM 实例。"""
    providers = {
        "openai": OpenAIModel,
        "deepseek": DeepSeekModel,
        "ollama": OllamaModel,
    }
    if provider not in providers:
        raise ValueError(f"不支持的 provider: {provider}，可选: {', '.join(providers)}")

    return providers[provider](model=model, api_key=api_key, base_url=base_url)


def main():
    parser = argparse.ArgumentParser(description="Agent 命令行工具")
    parser.add_argument(
        "--provider",
        choices=["openai", "deepseek", "ollama"],
        default="deepseek",
        help="LLM 提供商（默认: deepseek）",
    )
    parser.add_argument("--model", default=None, help="模型名称")
    parser.add_argument("--api-key", default=None, help="API Key（也可通过环境变量设置）")
    parser.add_argument("--base-url", default=None, help="API Base URL")
    parser.add_argument("--prompt", "-p", default=None, help="单次执行的提示词")
    parser.add_argument(
        "--workspace",
        "-w",
        default=str(PROJECT_ROOT),
        help="Agent 工作区根目录，限制文件与命令访问范围（默认: 项目根目录）",
    )
    args = parser.parse_args()

    try:
        workspace = set_workspace(args.workspace)
    except (NotADirectoryError, OSError) as e:
        print(f"工作区设置失败: {e}", file=sys.stderr)
        sys.exit(1)

    default_models = {
        "openai": "gpt-4o",
        "deepseek": "deepseek-chat",
        "ollama": "llama3",
    }
    model = args.model or default_models[args.provider]

    api_key = args.api_key or os.environ.get("OPENAI_API_KEY") or os.environ.get("DEEPSEEK_API_KEY")

    try:
        llm = create_llm(args.provider, model, api_key, args.base_url)
    except Exception as e:
        print(f"初始化 LLM 失败: {e}", file=sys.stderr)
        sys.exit(1)

    agent = Agent(llm)

    if args.prompt:
        print(agent.run(args.prompt))
        return

    print(f"Agent 已启动 [{args.provider}/{model}]，工作区: {workspace}")
    print("输入 'quit' 退出，'reset' 重置对话\n")
    while True:
        try:
            user_input = input("你: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n再见！")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("再见！")
            break
        if user_input.lower() == "reset":
            agent.reset()
            print("对话已重置。\n")
            continue

        print(f"\nAgent: {agent.run(user_input)}\n")


if __name__ == "__main__":
    main()
