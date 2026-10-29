from notifications import PushChannel


def test_new_push_channel_has_sent_nothing():
    assert PushChannel().sent == []
