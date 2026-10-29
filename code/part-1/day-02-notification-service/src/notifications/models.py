from dataclasses import dataclass


@dataclass(frozen=True)
class Notification:
    """A message to deliver; subject is used by email only."""

    to: str
    body: str
    subject: str | None = None


@dataclass(frozen=True)
class SendResult:
    """The outcome of sending through one channel."""

    channel: str
    ok: bool
    error: str | None = None


class UnknownChannelError(ValueError):
    """Raised when a channel name is not registered with the service."""


class ChannelError(Exception):
    """Raised by a channel that cannot deliver a notification."""
