# Gemini API pricing page, gemini-3.1-flash-lite, standard tier (checked 2026-11-20).
# The free tier charges nothing, so this cost is notional.
INPUT_PRICE_PER_MILLION = 0.25  # USD
OUTPUT_PRICE_PER_MILLION = 1.50  # USD, includes thinking tokens


def cost(usage: dict | None) -> float:
    """Notional USD cost of one reply, from its usage_metadata."""
    if usage is None:
        return 0.0
    return (
        usage["input_tokens"] * INPUT_PRICE_PER_MILLION
        + usage["output_tokens"] * OUTPUT_PRICE_PER_MILLION
    ) / 1_000_000
