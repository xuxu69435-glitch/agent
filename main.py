import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from agent import Agent
from llm import DeepSeekModel, OllamaModel, OpenAIModel
from tools.sandbox import set_workspace

PROJECT_ROOT = Path(__file__).resolve().parent

load_dotenv(PROJECT_ROOT / ".env", override=False)


PROVIDER_ENV_KEYS = {
    "openai": "OPENAI_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
}


def resolve_api_key(provider: str, cli_key: str | None) -> str | None:
    if cli_key:
        return cli_key
    env_var = PROVIDER_ENV_KEYS.get(provider)
    return os.environ.get(env_var) if env_var else None


def create_llm(provider: str, model: str, api_key: str | None, base_url: str | None):
    providers = {
        "openai": OpenAIModel,
        "deepseek": DeepSeekModel,
        "ollama": OllamaModel,
    }
    if provider not in providers:
        raise ValueError(f"不支持的 provider: {provider}，可选: {', '.join(providers)}")
    return providers[provider](model=model, api_key=api_key, base_url=base_url)


def main():
    parser = argparse.ArgumentParser(description="Repo Inspector Agent")
    parser.add_argument(
        "--provider",
        choices=["openai", "deepseek", "ollama"],
        default="deepseek",
        help="LLM 提供商（默认: deepseek）",
    )
    parser.add_argument("--model", default=None, help="模型名称")
    parser.add_argument("--api-key", default=None, help="API Key")
    parser.add_argument("--base-url", default=None, help="API Base URL")
    parser.add_argument("--prompt", "-p", default=None, help="单次执行的提示词")
    parser.add_argument(
        "--workspace",
        "-w",
        default=str(PROJECT_ROOT / "examples" / "sample_project"),
        help="待检查的仓库目录（默认: examples/sample_project）",
    )
    args = parser.parse_args()

    try:
        workspace = set_workspace(args.workspace)
    except (NotADirectoryError, OSError) as e:
        print(f"工作区设置失败: {e}", file=sys.stderr)
        sys.exit(1)

    default_models = {
        "openai": "gpt-4o",
        "deepseek": "deepseek-v4-pro",
        "ollama": "llama3",
    }
    model = args.model or default_models[args.provider]
    api_key = resolve_api_key(args.provider, args.api_key)

    if args.provider != "ollama" and not api_key:
        env_var = PROVIDER_ENV_KEYS[args.provider]
        print(
            f"缺少 API Key：请在 .env 中设置 {env_var}，或使用 --api-key 传入。",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        llm = create_llm(args.provider, model, api_key, args.base_url)
    except Exception as e:
        print(f"初始化 LLM 失败: {e}", file=sys.stderr)
        sys.exit(1)

    agent = Agent(llm)

    if args.prompt:
        print(agent.run(args.prompt))
        return

    print(f"Repo Inspector Agent [{args.provider}/{model}]")
    print(f"检查目标: {workspace}")
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
