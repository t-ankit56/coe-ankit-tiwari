from dataclasses import dataclass


@dataclass(frozen=True)
class Notification:
    to: str
    body: str
    subject: str | None = None
