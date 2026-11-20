from cost import cost


def test_zero_tokens_cost_nothing():
    assert cost({"input_tokens": 0, "output_tokens": 0}) == 0
