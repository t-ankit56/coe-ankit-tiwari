import prompts


def test_default_prompt_is_v2(monkeypatch):
    monkeypatch.delenv("PROMPT_VERSION", raising=False)
    assert prompts.get_prompt() is prompts.V2


def test_prompt_version_v1_picks_v1(monkeypatch):
    monkeypatch.setenv("PROMPT_VERSION", "v1")
    assert prompts.get_prompt() is prompts.V1


def test_both_prompts_take_context_and_question():
    expected = {"context", "question"}
    assert set(prompts.V1.input_variables) == expected
    assert set(prompts.V2.input_variables) == expected
