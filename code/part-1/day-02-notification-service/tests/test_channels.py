from notifications.channels import EmailChannel


def test_new_email_channel_has_sent_nothing():
    assert EmailChannel().sent == []
