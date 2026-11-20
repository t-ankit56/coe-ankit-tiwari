import prompts


def test_default_prompt_is_v2(monkeypatch):
    monkeypatch.delenv("PROMPT_VERSION", raising=False)
    assert prompts.get_prompt() is prompts.V2


def test_prompt_version_v1_picks_v1(monkeypatch):
    monkeypatch.setenv("PROMPT_VERSION", "v1")
    assert prompts.get_prompt() is prompts.V1
