from ai import router


def test_select_openai_model_prefers_cheap_for_simple_prompt(monkeypatch):
    monkeypatch.setenv("OPENAI_COST_AWARE_ROUTING", "1")
    monkeypatch.setenv("OPENAI_CHAT_MODEL_CHEAP", "gpt-4.1-nano")

    model = router._select_openai_model(
        configured_model="gpt-4o-mini",
        prompt="How do I calm down in 2 minutes?",
        max_tokens=320,
    )

    assert model == "gpt-4.1-nano"


def test_select_openai_model_uses_default_for_complex_prompt(monkeypatch):
    monkeypatch.setenv("OPENAI_COST_AWARE_ROUTING", "1")
    monkeypatch.setenv("OPENAI_CHAT_MODEL_CHEAP", "gpt-4.1-nano")

    model = router._select_openai_model(
        configured_model="gpt-4o-mini",
        prompt="Please analyze my weekly mood trends and build a monthly recovery strategy.",
        max_tokens=900,
    )

    assert model == "gpt-4o-mini"


def test_select_openai_model_can_be_disabled(monkeypatch):
    monkeypatch.setenv("OPENAI_COST_AWARE_ROUTING", "0")
    monkeypatch.setenv("OPENAI_CHAT_MODEL_CHEAP", "gpt-4.1-nano")

    model = router._select_openai_model(
        configured_model="gpt-4o-mini",
        prompt="Quick tip please",
        max_tokens=300,
    )

    assert model == "gpt-4o-mini"


def test_estimate_cost_uses_provider_defaults(monkeypatch):
    monkeypatch.setenv("OPENAI_DEFAULT_INPUT_COST_PER_MTOK", "0.25")
    monkeypatch.setenv("OPENAI_DEFAULT_OUTPUT_COST_PER_MTOK", "2.00")
    monkeypatch.delenv("AI_MODEL_PRICE_OVERRIDES", raising=False)

    cost = router._estimate_cost_usd(
        provider="openai",
        model="gpt-unknown",
        input_tokens=1000,
        output_tokens=500,
    )

    assert str(cost) == "0.001250"


def test_estimate_cost_uses_model_override(monkeypatch):
    monkeypatch.setenv("AI_MODEL_PRICE_OVERRIDES", "gpt-4.1-nano:0.20,0.80")

    cost = router._estimate_cost_usd(
        provider="openai",
        model="gpt-4.1-nano",
        input_tokens=2000,
        output_tokens=1000,
    )

    assert str(cost) == "0.001200"
