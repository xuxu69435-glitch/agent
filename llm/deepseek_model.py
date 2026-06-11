from .openai_model import OpenAIModel


class DeepSeekModel(OpenAIModel):
    """DeepSeek API 模型实现（兼容 OpenAI 接口）。"""

    DEFAULT_BASE_URL = "https://api.deepseek.com"

    def __init__(self, model: str = "deepseek-chat", api_key: str | None = None, base_url: str | None = None):
        super().__init__(
            model=model,
            api_key=api_key,
            base_url=base_url or self.DEFAULT_BASE_URL,
        )
