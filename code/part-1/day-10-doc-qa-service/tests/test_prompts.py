import prompts


def test_default_prompt_is_v2(monkeypatch):
    monkeypatch.delenv("PROMPT_VERSION", raising=False)
    assert prompts.get_prompt() is prompts.V2
