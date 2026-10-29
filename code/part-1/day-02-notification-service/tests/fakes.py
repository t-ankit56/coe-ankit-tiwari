class FakeChannel:
    def __init__(self):
        self.sent = []

    def send(self, notification):
        self.sent.append(notification)
