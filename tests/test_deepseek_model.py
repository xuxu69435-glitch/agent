from llm.deepseek_model import DeepSeekModel


def test_default_model_is_v4_pro():
    model = DeepSeekModel(api_key="test-key")

    assert model.model == "deepseek-v4-pro"
