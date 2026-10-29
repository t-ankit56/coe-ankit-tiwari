from dataclasses import dataclass


@dataclass(frozen=True)
class Notification:
    to: str
    body: str
    subject: str | None = None


@dataclass(frozen=True)
class SendResult:
    channel: str
    ok: bool
    error: str | None = None


class UnknownChannelError(ValueError):
    pass


class ChannelError(Exception):
    pass
