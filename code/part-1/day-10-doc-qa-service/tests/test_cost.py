from pytest import approx

from cost import cost


def test_zero_tokens_cost_nothing():
    assert cost({"input_tokens": 0, "output_tokens": 0}) == 0


def test_one_reply_costs_input_and_output_tokens_at_their_prices():
    # 2000 x $0.25/M + 500 x $1.50/M
    assert cost({"input_tokens": 2000, "output_tokens": 500}) == approx(0.00125)
